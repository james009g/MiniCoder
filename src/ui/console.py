from rich.panel import Panel
from src.core.config import console

def display_welcome_message():
    """Display the welcome message and instructions."""
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

def display_exit_message():
    """Display the exit message."""
    console.print("[bold #9333ea]👋 Goodbye! Happy coding![/bold #9333ea]")

def display_session_end():
    """Display the session end message."""
    console.print("[bold #9333ea]✨ Session finished. Thank you for using MiniCoder![/bold #9333ea]")
