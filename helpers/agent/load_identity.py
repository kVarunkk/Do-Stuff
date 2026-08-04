import os

def load_identity(path: str = "DOSTUFF.md") -> str:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are a general-purpose personal assistant agent built by Varun. Your name is 'DoStuff'."
