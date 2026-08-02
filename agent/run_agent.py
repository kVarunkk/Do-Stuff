from lib.memory.session_store import  SessionStore
from lib.tracing import  session_id_var, turn_id_var
import asyncio
import uuid
from lib.tracing import tracer
from opentelemetry.trace import Status, StatusCode
from helpers.agent.constants import COMMANDS, MAX_ITERATIONS
from helpers.agent.extract_text import extract_text
from helpers.agent.print_history import print_history
from agent.call_agent import call_agent
from agent.run_tool import run_tool
from helpers.agent.manage_context import compact_context
from helpers.agent.get_model_token_limit import get_model_token_limit
from lib.memory.memory_store import MemoryStore
from helpers.agent.save_memories_and_exit import save_memories_and_exit
from lib.exceptions import ConfirmationRequired
from helpers.agent.append_step import append_step
import copy
from lib.mcp.mcp_client import MCPClient

async def run_agent(session_id: str, user_id: str, store: SessionStore, memory_store: MemoryStore, system_instructions:str, mcp_client: MCPClient) -> None:
    session_id_var.set(session_id)
    steps_history = await store.load(session_id)
    last_input_tokens = 0
    token_limit = await get_model_token_limit()
    context_token_threshold = int(token_limit * 0.8)
    keep_recent_token_budget = int(context_token_threshold * 0.15)
    working_history = copy.deepcopy(steps_history)
    compaction_notes = ""

    try:
        while True:
            user_text = await asyncio.to_thread(input, "User: ")
    
            if not user_text:
                continue
    
            command = user_text.strip().lower()
    
            if command == "/exit":
                await save_memories_and_exit(steps_history, user_id, memory_store)
                break
    
            if command == "/history":
                print_history(steps_history)
                continue
    
            if command == "/clear":
                steps_history = []
                await store.save(session_id, steps_history)
                print("History cleared.")
                continue
    
            if command == "/help":
                print(f"Commands: {', '.join(sorted(COMMANDS))}")
                continue
    
            turn_id = str(uuid.uuid4())
            turn_id_var.set(turn_id)
    
            user_step = {
                    "type": "user_input",
                    "content": [{"type": "text", "text": user_text}],
                }
           
            await append_step(user_step, steps_history, working_history, session_id, store)
    
            memories = await memory_store.query(user_id, query_text=user_text, top_k=5)
            memory_text = "\n".join(f"- {m['key']}: {m['value']}" for m in memories)
    
            dynamic_system_instruction = system_instructions
            if memory_text:
                dynamic_system_instruction += f"\n\nRelevant context about this user:\n{memory_text}"
    
    
            # print(f'SYSTEM INSTRUCTIONS: {dynamic_system_instruction}')
                
            iteration = 0
    
            with tracer.start_as_current_span("turn") as turn_span:
                turn_span.set_attribute("session_id", session_id)
                turn_span.set_attribute("turn_id", turn_id)
                turn_span.set_attribute("user_input", user_text)
    
                while iteration < MAX_ITERATIONS:
                    iteration += 1
    
                    with tracer.start_as_current_span("iteration") as iter_span:
                        iter_span.set_attribute("iteration_number", iteration)

                        # print(f"LAST INPUT TOKENS: {last_input_tokens}")

                        if last_input_tokens > context_token_threshold:
                            working_history, new_summary = await compact_context(working_history, keep_recent_token_budget)
                            compaction_notes = f"{compaction_notes}\n{new_summary}".strip()

                            with tracer.start_as_current_span("context_compaction") as compaction_span:
                                compaction_span.set_attribute("steps_after", len(working_history))
                        
                        # agent call  
                        interaction = await call_agent(steps_history=working_history, system_instruction=dynamic_system_instruction + (f"\n\n[Summary of earlier conversation]: {compaction_notes}" if compaction_notes else ""))
    
                        usage = getattr(interaction, "usage", None)
                        if usage:
                            last_input_tokens = getattr(usage, "total_input_tokens", last_input_tokens)
        
                        interaction_steps = getattr(interaction, "steps", None)
            
                        if not interaction_steps:
                            iter_span.set_status(Status(StatusCode.OK))
                            continue
            
                        for step in interaction_steps:
                            dumped = step.model_dump()
                            await append_step(dumped, steps_history, working_history, session_id, store)
            
                        last_step = interaction_steps[-1]
                        if getattr(last_step, "type", None) == "model_output":
                            final_text = extract_text(last_step)
                            if final_text is not None:
                                turn_span.set_attribute("outcome", "success")
                                turn_span.set_status(Status(StatusCode.OK))
                                iter_span.set_status(Status(StatusCode.OK))
                                print(f"Agent: {final_text}")
                                break
            
                        function_calls = [
                            (
                                getattr(step, "name", None),
                                getattr(step, "arguments", None) or {},
                                getattr(step, "id", None),
                            )
                            for step in interaction_steps
                            if getattr(step, "type", None) == "function_call"
                        ]
            
                        if not function_calls:
                            iter_span.set_status(Status(StatusCode.OK)) 
                            continue
            
                        for fn_name, fn_args, _ in function_calls:
                            print(f"-> Calling local tool: {fn_name}({fn_args})")
            
                        results = await asyncio.gather(
                            *(run_tool(fn_name=fn_name, fn_args=dict(fn_args), mcp_client=mcp_client) for fn_name, fn_args, _ in function_calls),
                            return_exceptions=True,
                        )

                        final_results = []
                        for (fn_name, fn_args, fn_id), result in zip(function_calls, results):
                            if isinstance(result, ConfirmationRequired):
                                print(f"\nConfirmation needed: {result.message}")
                                confirm = await asyncio.to_thread(input, "Allow this? [y/n]: ")
                        
                                if confirm.strip().lower() == "y":
                                    resumed_args = {**fn_args, **result.resume_args}
                                    result = await run_tool(fn_name=fn_name, fn_args=resumed_args, mcp_client=mcp_client)
                                else:
                                    result = "Error: User declined to allow this action."
                        
                            elif isinstance(result, Exception):
                                result = f"Error: {result}"
                        
                            final_results.append((fn_name, fn_id, result))
                        
                        for fn_name, fn_id, result in final_results:
                            result_step = {
                                "name": fn_name,
                                "result": result,
                                "id": fn_id,
                                "type": "function_result",
                            }
                            await append_step(result_step, steps_history, working_history, session_id, store)
                            iter_span.set_status(Status(StatusCode.OK))
            
                else:
                    turn_span.set_attribute("outcome", "max_iterations_exceeded")  
                    turn_span.set_status(Status(StatusCode.ERROR, "max_iterations_exceeded"))

    except KeyboardInterrupt:
        raise

           