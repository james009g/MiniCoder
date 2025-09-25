import os
from src.core.config import console, prompt_session
from src.core.models import SYSTEM_PROMPT
from src.utils.file_operations import (
    normalize_path, read_local_file, add_directory_to_conversation
)
from src.api.handler import stream_openai_response
from src.ui.console import display_welcome_message, display_exit_message, display_session_end

# --------------------------------------------------------------------------------
# Conversation state
# --------------------------------------------------------------------------------
conversation_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

# --------------------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------------------

def try_handle_add_command(user_input: str) -> bool:
    prefix = "/add "
    if user_input.strip().lower().startswith(prefix):
        path_to_add = user_input[len(prefix):].strip()
        try:
            normalized_path = normalize_path(path_to_add)
            if os.path.isdir(normalized_path):
                # Handle entire directory
                add_directory_to_conversation(normalized_path, conversation_history)
            else:
                # Handle a single file as before
                content = read_local_file(normalized_path)
                conversation_history.append({
                    "role": "system",
                    "content": f"Content of file '{normalized_path}':\n\n{content}"
                })
                console.print(f"[bold blue]✓[/bold blue] Added file '[bright_cyan]{normalized_path}[/bright_cyan]' to conversation.\n")
        except OSError as e:
            console.print(f"[bold red]✗[/bold red] Could not add path '[bright_cyan]{path_to_add}[/bright_cyan]': {e}\n")
        return True
    return False

# --------------------------------------------------------------------------------
# Main interactive loop
# --------------------------------------------------------------------------------

def main():
    # Display welcome message
    display_welcome_message()

    while True:
        try:
            user_input = prompt_session.prompt("💜 You> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[#f59e0b]👋 Exiting gracefully...[/#f59e0b]")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            display_exit_message()
            break

        if try_handle_add_command(user_input):
            continue

        response_data = stream_openai_response(user_input, conversation_history)
        
        if response_data.get("error"):
            console.print(f"[bold #ef4444]❌ Error: {response_data['error']}[/bold #ef4444]")

    display_session_end()

if __name__ == "__main__":
    main()