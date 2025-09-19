import os
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.theme import Theme
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PromptStyle

# Load environment variables
load_dotenv()

# Define a custom theme for rich
custom_theme = Theme({
    # Primary colors
    "primary": "#9333ea",           # Purple
    "secondary": "#c084fc",         # Light purple
    "accent": "#f472b6",            # Pink
    "success": "#10b981",           # Green
    "warning": "#f59e0b",           # Amber
    "error": "#ef4444",             # Red
    "info": "#3b82f6",              # Blue
    "muted": "#6b7280",             # Gray
    
    # UI elements
    "heading": "bold #9333ea",      # Bold purple
    "subheading": "bold #c084fc",   # Bold light purple
    "border": "#9333ea",            # Purple border
    "panel_title": "bold #f472b6",  # Bold pink title
    "highlight": "#f472b6",         # Pink highlight
    "code": "#10b981",              # Green code
    "prompt": "bold #9333ea",       # Bold purple prompt
})

# Initialize Rich console with custom theme
console = Console(theme=custom_theme)

# Prompt toolkit style
prompt_session = PromptSession(
    style=PromptStyle.from_dict({
        'prompt': '#9333ea bold',                   # Purple prompt
        'completion-menu.completion': 'bg:#4c1d95 fg:#ffffff',
        'completion-menu.completion.current': 'bg:#9333ea fg:#ffffff bold',
    })
)

# Configure OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),)