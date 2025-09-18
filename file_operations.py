

import os
from pathlib import Path
from rich.panel import Panel
from config import console

# --------------------------------------------------------------------------------
# File Operations
# --------------------------------------------------------------------------------

def read_local_file(file_path: str) -> str:
    """Return the text content of a local file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def create_file(path: str, content: str):
    """Create (or overwrite) a file at 'path' with the given 'content'."""
    file_path = Path(path)
    
    # Security checks
    if any(part.startswith('~') for part in file_path.parts):
        raise ValueError("Home directory references not allowed")
    normalized_path = normalize_path(str(file_path))
    
    # Validate reasonable file size for operations
    if len(content) > 5_000_000:  # 5MB limit
        raise ValueError("File content exceeds 5MB size limit")
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    console.print(f"[bold blue]✓[/bold blue] Created/updated file at '[bright_cyan]{file_path}[/bright_cyan]'")

def apply_diff_edit(path: str, original_snippet: str, new_snippet: str):
    """Reads the file at 'path', replaces the first occurrence of 'original_snippet' with 'new_snippet', then overwrites."""
    try:
        content = read_local_file(path)
        
        # Verify we're replacing the exact intended occurrence
        occurrences = content.count(original_snippet)
        if occurrences == 0:
            # Try to find a close match with some tolerance
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if original_snippet.strip() in line.strip():
                    console.print(f"[bold yellow]⚠ Found similar content at line {i+1}[/bold yellow]")
                    console.print(f"[dim]Original: {line.strip()}[/dim]")
                    console.print(f"[dim]Looking for: {original_snippet.strip()}[/dim]")
                    break
            raise ValueError("Original snippet not found")
        if occurrences > 1:
            console.print(f"[bold yellow]⚠ Multiple matches ({occurrences}) found - using first occurrence[/bold yellow]")
        
        updated_content = content.replace(original_snippet, new_snippet, 1)
        create_file(path, updated_content)
        console.print(f"[bold blue]✓[/bold blue] Applied diff edit to '[bright_cyan]{path}[/bright_cyan]'")

    except FileNotFoundError:
        console.print(f"[bold red]✗[/bold red] File not found for diff editing: '[bright_cyan]{path}[/bright_cyan]'")
    except ValueError as e:
        console.print(f"[bold yellow]⚠[/bold yellow] {str(e)} in '[bright_cyan]{path}[/bright_cyan]'. No changes made.")
        console.print("\n[bold blue]Expected snippet:[/bold blue]")
        console.print(Panel(original_snippet, title="Expected", border_style="blue", title_align="left"))
        console.print("\n[bold blue]Actual file content:[/bold blue]")
        console.print(Panel(content, title="Actual", border_style="yellow", title_align="left"))

def normalize_path(path_str: str) -> str:
    """Return a canonical, absolute version of the path with security checks."""
    path = Path(path_str).resolve()
    
    # Prevent directory traversal attacks
    if ".." in path.parts:
        raise ValueError(f"Invalid path: {path_str} contains parent directory references")
    
    return str(path)

def is_binary_file(file_path: str, peek_size: int = 1024) -> bool:
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(peek_size)
        # If there is a null byte in the sample, treat it as binary
        if b'\0' in chunk:
            return True
        return False
    except Exception:
        # If we fail to read, just treat it as binary to be safe
        return True

        def add_directory_to_conversation(directory_path: str, conversation_history):
    """Add all files in a directory to the conversation context."""
    excluded_files = {
        # Python specific
        ".DS_Store", "Thumbs.db", ".gitignore", ".python-version",
        "uv.lock", ".uv", "uvenv", ".uvenv", ".venv", "venv",
        "__pycache__", ".pytest_cache", ".coverage", ".mypy_cache",
        # Node.js / Web specific
        "node_modules", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        ".next", ".nuxt", "dist", "build", ".cache", ".parcel-cache",
        ".turbo", ".vercel", ".output", ".contentlayer",
        # Build outputs
        "out", "coverage", ".nyc_output", "storybook-static",
        # Environment and config
        ".env", ".env.local", ".env.development", ".env.production",
        # Misc
        ".git", ".svn", ".hg", "CVS"
    }
    excluded_extensions = {
        # Binary and media files
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".avif",
        ".mp4", ".webm", ".mov", ".mp3", ".wav", ".ogg",
        ".zip", ".tar", ".gz", ".7z", ".rar",
        ".exe", ".dll", ".so", ".dylib", ".bin",
        # Documents
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        # Python specific
        ".pyc", ".pyo", ".pyd", ".egg", ".whl",
        # UV specific
        ".uv", ".uvenv",
        # Database and logs
        ".db", ".sqlite", ".sqlite3", ".log",
        # IDE specific
        ".idea", ".vscode",
        # Web specific
        ".map", ".chunk.js", ".chunk.css",
        ".min.js", ".min.css", ".bundle.js", ".bundle.css",
        # Cache and temp files
        ".cache", ".tmp", ".temp",
        # Font files
        ".ttf", ".otf", ".woff", ".woff2", ".eot"
    }
    
    with console.status("[bold bright_blue]🔍 Scanning directory...[/bold bright_blue]") as status:
        skipped_files = []
        added_files = []
        total_files_processed = 0
        max_files = 1000  # Reasonable limit for files to process
        max_file_size = 5_000_000  # 5MB limit

        for root, dirs, files in os.walk(directory_path):
            if total_files_processed >= max_files:
                console.print(f"[bold yellow]⚠[/bold yellow] Reached maximum file limit ({max_files})")
                break

            status.update(f"[bold bright_blue]🔍 Scanning {root}...[/bold bright_blue]")
            # Skip hidden directories and excluded directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in excluded_files]

            for file in files:
                if total_files_processed >= max_files:
                    break

                if file.startswith('.') or file in excluded_files:
                    skipped_files.append(os.path.join(root, file))
                    continue

                _, ext = os.path.splitext(file)
                if ext.lower() in excluded_extensions:
                    skipped_files.append(os.path.join(root, file))
                    continue

                full_path = os.path.join(root, file)

                try:
                    # Check file size before processing
                    if os.path.getsize(full_path) > max_file_size:
                        skipped_files.append(f"{full_path} (exceeds size limit)")
                        continue

                    # Check if it's binary
                    if is_binary_file(full_path):
                        skipped_files.append(full_path)
                        continue

                    normalized_path = normalize_path(full_path)
                    content = read_local_file(normalized_path)
                    conversation_history.append({
                        "role": "system",
                        "content": f"Content of file '{normalized_path}':\n\n{content}"
                    })
                    added_files.append(normalized_path)
                    total_files_processed += 1

                except OSError:
                    skipped_files.append(full_path)

        console.print(f"[bold blue]✓[/bold blue] Added folder '[bright_cyan]{directory_path}[/bright_cyan]' to conversation.")
        if added_files:
            console.print(f"\n[bold bright_blue]📁 Added files:[/bold bright_blue] [dim]({len(added_files)} of {total_files_processed})[/dim]")
            for f in added_files:
                console.print(f"  [bright_cyan]📄 {f}[/bright_cyan]")
        if skipped_files:
            console.print(f"\n[bold yellow]⏭ Skipped files:[/bold yellow] [dim]({len(skipped_files)})[/dim]")
            for f in skipped_files[:10]:  # Show only first 10 to avoid clutter
                console.print(f"  [yellow dim]⚠ {f}[/yellow dim]")
            if len(skipped_files) > 10:
                console.print(f"  [dim]... and {len(skipped_files) - 10} more[/dim]")
        console.print()