import os
from rich.panel import Panel
from config import console, prompt_session
from models import SYSTEM_PROMPT
from file_operations import (
    normalize_path, read_local_file, add_directory_to_conversation
)
from api_handler import stream_openai_response

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
    # Create a beautiful gradient-style welcome panel
    welcome_text = """[bold #9333ea]✨ MiniCoder[/bold #9333ea] [#f472b6]with Tool Calling[/#f472b6]"""
    
    console.print(Panel.fit(
        welcome_text,
        border_style="#9333ea",
        padding=(1, 2),
        title="[bold #f472b6]🤖 AI Code Assistant[/bold #f472b6]",
        title_align="center"
    ))
    
    # Create an elegant instruction panel
    instructions = """[bold #c084fc]📁 File Operations:[/bold #c084fc]
  • [#f472b6]/add path/to/file[/#f472b6] - Include a single file in conversation
  • [#f472b6]/add path/to/folder[/#f472b6] - Include all files in a folder
  • [#6b7280]The AI can automatically read and create files using function calls[/#6b7280]

[bold #c084fc]🎯 Commands:[/bold #c084fc]
  • [#f472b6]exit[/#f472b6] or [#f472b6]quit[/#f472b6] - End the session
  • Just ask naturally - the AI will handle file operations automatically!"""
    
    console.print(Panel(
        instructions,
        border_style="#9333ea",
        padding=(1, 2),
        title="[bold #f472b6]💡 How to Use[/bold #f472b6]",
        title_align="left"
    ))
    console.print()

    while True:
        try:
            user_input = prompt_session.prompt("💜 You> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[#f59e0b]👋 Exiting gracefully...[/#f59e0b]")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            console.print("[bold #9333ea]👋 Goodbye! Happy coding![/bold #9333ea]")
            break

        if try_handle_add_command(user_input):
            continue

        response_data = stream_openai_response(user_input, conversation_history)
        
        if response_data.get("error"):
            console.print(f"[bold #ef4444]❌ Error: {response_data['error']}[/bold #ef4444]")

    console.print("[bold #9333ea]✨ Session finished. Thank you for using MiniCoder![/bold #9333ea]")

if __name__ == "__main__":
    main()