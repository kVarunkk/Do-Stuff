
import asyncio
from agent.call_agent import call_agent
from helpers.agent.constants import MAX_ITERATIONS, SYSTEM_INSTRUCTION_FOR_SELF_LEARNING
from helpers.memory.format_transcript import format_transcript
from lib.exceptions import ConfirmationRequired
from lib.mcp.mcp_client import MCPClient
from agent.run_tool import run_tool
from lib.tracing import tracer
import uuid
from lib.tracing import  session_id_var, turn_id_var
from opentelemetry.trace import Status, StatusCode

async def learn_from_session(steps_history: list[dict], mcp_client: MCPClient, session_id: str):
    conversation_text = format_transcript(steps_history, type="skill_update")
    if not conversation_text.strip() or len(conversation_text) < 100:
        print("[Learning Loop] Transcript too short for skill reflection.")
        return

    user_prompt = f"""Analyze the following session transcript and apply necessary skill updates or creations:

<session_transcript>
{conversation_text}
</session_transcript>

Proceed step-by-step:
1. List existing skills in the `skills/` directory.
2. Read relevant existing `SKILL.md` files if updating.
3. Synthesize and write any new or updated `SKILL.md` file using your file tools.
4. End with a brief text summary of what was created or updated (or explain why no skill changes were needed)."""

    await learn_from_session_loop(user_prompt, system_instruction=SYSTEM_INSTRUCTION_FOR_SELF_LEARNING, mcp_client=mcp_client, session_id=session_id)
   

async def learn_from_session_loop(user_prompt: str, system_instruction: str, mcp_client: MCPClient, session_id: str):
    current_session_history = [
        {
            "type": "user_input",
            "content": [{"type": "text", "text": user_prompt}],
        }
    ]
    session_id_var.set(session_id)
    turn_id = str(uuid.uuid4())
    turn_id_var.set(turn_id)
    iteration = 0

    with tracer.start_as_current_span("turn") as turn_span:
        turn_span.set_attribute("session_id", session_id)
        turn_span.set_attribute("turn_type", "learning_loop")
        turn_span.set_attribute("turn_id", turn_id)
        turn_span.set_attribute("user_input", user_prompt)

        while iteration < MAX_ITERATIONS:
            iteration += 1

            with tracer.start_as_current_span("iteration") as iter_span:
                iter_span.set_attribute("iteration_number", iteration)


                interaction = await call_agent(steps_history=current_session_history, system_instruction=system_instruction)
                interaction_steps = getattr(interaction, "steps", None)
                if not interaction_steps:
                    continue
                for step in interaction_steps:
                    dumped = step.model_dump()
                    current_session_history.append(dumped)
                last_step = interaction_steps[-1]
        
                if getattr(last_step, "type", None) == "model_output":
                        turn_span.set_attribute("outcome", "success")
                        turn_span.set_status(Status(StatusCode.OK))
                        iter_span.set_status(Status(StatusCode.OK))
                        print("Agent: Model output received. Ending the learning loop.")
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
                    current_session_history.append(result_step)
                    iter_span.set_status(Status(StatusCode.OK))
    
        else: 
            print(f"Reached maximum iterations ({MAX_ITERATIONS}) without receiving a model output. Ending the learning loop.")
            turn_span.set_attribute("outcome", "max_iterations_exceeded")  
            turn_span.set_status(Status(StatusCode.ERROR, "max_iterations_exceeded"))        