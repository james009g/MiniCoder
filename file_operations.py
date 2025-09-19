

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
    console.print(f"[bold #10b981]✓[/bold #10b981] Created/updated file at '[#f472b6]{file_path}[/#f472b6]'")

def apply_diff_edit(path: str, original_snippet: str, new_snippet: str):
    """Reads the file at 'path', replaces the first occurrence of 'original_snippet' with 'new_snippet', then overwrites."""
    try:
        content = read_local_file(path)
        
        # Verify we're replacing the exact intended occurrence
        occurrences = content.count(original_snippet)
        if occurrences == 0:
            # Try to find a close match with some tolerance
            lines = content.split('\n')
            console.print(f"[bold #f59e0b]⚠ Original snippet not found exactly. Searching for similar content...[/bold #f59e0b]")
            
            # Try multi-line matching
            original_lines = original_snippet.strip().split('\n')
            best_match_line = -1
            best_match_score = 0
            
            for i in range(len(lines) - len(original_lines) + 1):
                match_score = 0
                for j, orig_line in enumerate(original_lines):
                    if i + j < len(lines) and orig_line.strip() in lines[i + j].strip():
                        match_score += 1
                
                if match_score > best_match_score:
                    best_match_score = match_score
                    best_match_line = i
            
            if best_match_score > 0:
                console.print(f"[bold #f59e0b]⚠ Found partial match starting at line {best_match_line + 1}[/bold #f59e0b]")
                console.print(f"[#6b7280]Match score: {best_match_score}/{len(original_lines)} lines[/#6b7280]")
                console.print(f"[#6b7280]Looking for: {original_snippet.strip()}[/#6b7280]")
                console.print(f"[#6b7280]Found around line {best_match_line + 1}: {lines[best_match_line].strip() if best_match_line < len(lines) else 'N/A'}[/#6b7280]")
            
            raise ValueError(f"Original snippet not found. Best match score: {best_match_score}/{len(original_lines)}")
        
        if occurrences > 1:
            console.print(f"[bold #f59e0b]⚠ Multiple matches ({occurrences}) found - using first occurrence[/bold #f59e0b]")
        
        updated_content = content.replace(original_snippet, new_snippet, 1)
        create_file(path, updated_content)
        console.print(f"[bold #10b981]✓[/bold #10b981] Applied diff edit to '[#f472b6]{path}[/#f472b6]'")

    except FileNotFoundError:
        console.print(f"[bold #ef4444]✗[/bold #ef4444] File not found for diff editing: '[#f472b6]{path}[/#f472b6]'")
        raise
    except ValueError as e:
        console.print(f"[bold #f59e0b]⚠[/bold #f59e0b] {str(e)} in '[#f472b6]{path}[/#f472b6]'. No changes made.")
        console.print("\n[bold #c084fc]Expected snippet:[/bold #c084fc]")
        console.print(Panel(original_snippet, title="Expected", border_style="#9333ea", title_align="left"))
        console.print("\n[bold #c084fc]Actual file content:[/bold #c084fc]")
        console.print(Panel(content, title="Actual", border_style="#f59e0b", title_align="left"))
        raise

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

        console.print(f"[bold #10b981]✓[/bold #10b981] Added folder '[#f472b6]{directory_path}[/#f472b6]' to conversation.")
        if added_files:
            console.print(f"\n[bold #9333ea]📁 Added files:[/bold #9333ea] [#6b7280]({len(added_files)} of {total_files_processed})[/#6b7280]")
            for f in added_files:
                console.print(f"  [#f472b6]📄 {f}[/#f472b6]")
        if skipped_files:
            console.print(f"\n[bold #f59e0b]⏭ Skipped files:[/bold #f59e0b] [#6b7280]({len(skipped_files)})[/#6b7280]")
            for f in skipped_files[:10]:  # Show only first 10 to avoid clutter
                console.print(f"  [#f59e0b dim]⚠ {f}[/#f59e0b dim]")
            if len(skipped_files) > 10:
                console.print(f"  [#6b7280]... and {len(skipped_files) - 10} more[/#6b7280]")
        console.print()

def ensure_file_in_context(file_path: str, conversation_history) -> bool:
    try:
        normalized_path = normalize_path(file_path)
        content = read_local_file(normalized_path)
        file_marker = f"Content of file '{normalized_path}'"
        if not any((isinstance(msg.get("content"), str) and file_marker in msg["content"]) for msg in conversation_history):
            conversation_history.append({
                "role": "system",
                "content": f"{file_marker}:\n\n{content}"
            })
        return True
    except OSError:
        console.print(f"[bold #ef4444]✗[/bold #ef4444] Could not read file '[#f472b6]{file_path}[/#f472b6]' for editing context")
        return False

