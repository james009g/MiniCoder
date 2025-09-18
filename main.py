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
    welcome_text = """[bold bright_blue]🐋 DeepSeek Engineer[/bold bright_blue] [bright_cyan]with Function Calling[/bright_cyan]
[dim blue]Powered by DeepSeek-R1 with Chain-of-Thought Reasoning[/dim blue]"""
    
    console.print(Panel.fit(
        welcome_text,
        border_style="bright_blue",
        padding=(1, 2),
        title="[bold bright_cyan]🤖 AI Code Assistant[/bold bright_cyan]",
        title_align="center"
    ))
    
    # Create an elegant instruction panel
    instructions = """[bold bright_blue]📁 File Operations:[/bold bright_blue]
  • [bright_cyan]/add path/to/file[/bright_cyan] - Include a single file in conversation
  • [bright_cyan]/add path/to/folder[/bright_cyan] - Include all files in a folder
  • [dim]The AI can automatically read and create files using function calls[/dim]

[bold bright_blue]🎯 Commands:[/bold bright_blue]
  • [bright_cyan]exit[/bright_cyan] or [bright_cyan]quit[/bright_cyan] - End the session
  • Just ask naturally - the AI will handle file operations automatically!"""
    
    console.print(Panel(
        instructions,
        border_style="blue",
        padding=(1, 2),
        title="[bold blue]💡 How to Use[/bold blue]",
        title_align="left"
    ))
    console.print()

    while True:
        try:
            user_input = prompt_session.prompt("🔵 You> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold yellow]👋 Exiting gracefully...[/bold yellow]")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            console.print("[bold bright_blue]👋 Goodbye! Happy coding![/bold bright_blue]")
            break

        if try_handle_add_command(user_input):
            continue

        response_data = stream_openai_response(user_input, conversation_history)
        
        if response_data.get("error"):
            console.print(f"[bold red]❌ Error: {response_data['error']}[/bold red]")

    console.print("[bold blue]✨ Session finished. Thank you for using DeepSeek Engineer![/bold blue]")

if __name__ == "__main__":
    main()