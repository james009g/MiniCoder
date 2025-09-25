#!/usr/bin/env python3

# Test imports
try:
    print("Testing imports...")
    from src.core.config import console
    print("✓ Imported src.core.config")
    
    from src.core.models import SYSTEM_PROMPT
    print("✓ Imported src.core.models")
    
    from src.utils.file_operations import normalize_path, read_local_file
    print("✓ Imported src.utils.file_operations")
    
    from src.api.handler import stream_openai_response
    print("✓ Imported src.api.handler")
    
    from src.tools.definitions import tools
    print("✓ Imported src.tools.definitions")
    
    from src.ui.console import display_welcome_message
    print("✓ Imported src.ui.console")
    
    print("\nAll imports successful!")
except Exception as e:
    print(f"Error: {e}")
