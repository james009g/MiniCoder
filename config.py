import os
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PromptStyle

# Load environment variables
load_dotenv()

# Initialize Rich console and prompt session
console = Console()
prompt_session = PromptSession(
    style=PromptStyle.from_dict({
        'prompt': '#0066ff bold',  # Bright blue prompt
        'completion-menu.completion': 'bg:#1e3a8a fg:#ffffff',
        'completion-menu.completion.current': 'bg:#3b82f6 fg:#ffffff bold',
    })
)

# Configure OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),)