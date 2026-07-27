def print_history(steps_history: list[dict]) -> None:
    if not steps_history:
        print("(no history yet)")
        return
    for i, step in enumerate(steps_history):
        print(f"[{i}] {step}")  