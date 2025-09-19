import json
import time
from config import client, console
from tools import tools
from file_operations import (
    read_local_file, normalize_path, create_file, 
    apply_diff_edit, ensure_file_in_context
)

# --------------------------------------------------------------------------------
# Tool Execution
# --------------------------------------------------------------------------------

def execute_function_call_dict(tool_call_dict, conversation_history) -> str:
    """Execute a function call from a dictionary format and return the result as a string."""
    try:
        # Debug: Print the tool call structure
        console.print(f"[dim]Debug: Tool call structure: {tool_call_dict}[/dim]")
        function_name = tool_call_dict.get("function", {}).get("name")
        if not function_name:
            return "Error: No function name provided in tool call"
        
        arguments_str = tool_call_dict.get("function", {}).get("arguments", "{}")
        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError as e:
            return f"Error parsing function arguments: {str(e)}"
        
        if function_name == "read_file":
            file_path = arguments["file_path"]
            normalized_path = normalize_path(file_path)
            content = read_local_file(normalized_path)
            return f"Content of file '{normalized_path}':\n\n{content}"
            
        elif function_name == "read_multiple_files":
            file_paths = arguments["file_paths"]
            results = []
            for file_path in file_paths:
                try:
                    normalized_path = normalize_path(file_path)
                    content = read_local_file(normalized_path)
                    results.append(f"Content of file '{normalized_path}':\n\n{content}")
                except OSError as e:
                    results.append(f"Error reading '{file_path}': {e}")
            return "\n\n" + "="*50 + "\n\n".join(results)
            
        elif function_name == "create_file":
            file_path = arguments["file_path"]
            content = arguments["content"]
            create_file(file_path, content)
            return f"Successfully created file '{file_path}'"
            
        elif function_name == "create_multiple_files":
            files = arguments["files"]
            created_files = []
            for file_info in files:
                create_file(file_info["path"], file_info["content"])
                created_files.append(file_info["path"])
            return f"Successfully created {len(created_files)} files: {', '.join(created_files)}"
            
        elif function_name == "edit_file":
            file_path = arguments["file_path"]
            original_snippet = arguments["original_snippet"]
            new_snippet = arguments["new_snippet"]
            
            # Ensure file is in context first
            if not ensure_file_in_context(file_path, conversation_history):
                return f"Error: Could not read file '{file_path}' for editing"
            
            # Try to apply the edit
            try:
                apply_diff_edit(file_path, original_snippet, new_snippet)
                return f"Successfully edited file '{file_path}'"
            except Exception as e:
                # Provide more detailed error information
                error_details = f"Error editing file '{file_path}': {str(e)}"
                console.print(f"[bold red]✗[/bold red] {error_details}")
                
                # Show the actual file content for debugging
                try:
                    current_content = read_local_file(file_path)
                    console.print("\n[bold blue]Current file content:[/bold blue]")
                    console.print(Panel(current_content, title="Current Content", border_style="yellow", title_align="left"))
                except Exception as read_error:
                    console.print(f"[dim]Could not read file for debugging: {read_error}[/dim]")
                
                return error_details
            
        else:
            return f"Unknown function: {function_name}"
            
    except Exception as e:
        function_name = tool_call_dict.get("function", {}).get("name", "unknown")
        return f"Error executing {function_name}: {str(e)}"

def trim_conversation_history(conversation_history):
    """Trim conversation history to prevent token limit issues while preserving tool call sequences"""
    if len(conversation_history) <= 20:  # Don't trim if conversation is still small
        return
        
    # Always keep the system prompt
    system_msgs = [msg for msg in conversation_history if msg["role"] == "system"]
    other_msgs = [msg for msg in conversation_history if msg["role"] != "system"]
    
    # Keep only the last 15 messages to prevent token overflow
    if len(other_msgs) > 15:
        other_msgs = other_msgs[-15:]
    
    # Rebuild conversation history
    conversation_history.clear()
    conversation_history.extend(system_msgs + other_msgs)

def stream_openai_response(user_message: str, conversation_history):
    # Add the user message to conversation history
    conversation_history.append({"role": "user", "content": user_message})
    
    # Trim conversation history if it's getting too long
    trim_conversation_history(conversation_history)

    try:
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history,
            tools=tools,
            max_completion_tokens=2000,
            stream=True
        )

        console.print("\n[bold #9333ea]✨ Thinking...[/bold #9333ea]")
        reasoning_started = False
        final_content = ""
        tool_calls = []

        for chunk in stream:
            # Handle reasoning content if available
            if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                if not reasoning_started:
                    console.print("\n[bold #c084fc]💭 Reasoning:[/bold #c084fc]")
                    reasoning_started = True
                console.print(chunk.choices[0].delta.reasoning_content, end="")
            elif chunk.choices[0].delta.content:
                if reasoning_started:
                    console.print("\n")  # Add spacing after reasoning
                    console.print("\n[bold #f472b6]🤖 Assistant>[/bold #f472b6] ", end="")
                    reasoning_started = False
                final_content += chunk.choices[0].delta.content
                console.print(chunk.choices[0].delta.content, end="")
            elif chunk.choices[0].delta.tool_calls:
                # Handle tool calls
                for tool_call_delta in chunk.choices[0].delta.tool_calls:
                    if tool_call_delta.index is not None:
                        # Ensure we have enough tool_calls
                        while len(tool_calls) <= tool_call_delta.index:
                            tool_calls.append({
                                "id": "",
                                "type": "function",
                                "function": {"name": "", "arguments": ""}
                            })
                        
                        if tool_call_delta.id:
                            tool_calls[tool_call_delta.index]["id"] = tool_call_delta.id
                        if tool_call_delta.function:
                            if tool_call_delta.function.name:
                                tool_calls[tool_call_delta.index]["function"]["name"] += tool_call_delta.function.name
                            if tool_call_delta.function.arguments:
                                tool_calls[tool_call_delta.index]["function"]["arguments"] += tool_call_delta.function.arguments

        console.print()  # New line after streaming

        # Store the assistant's response in conversation history
        assistant_message = {
            "role": "assistant",
            "content": final_content if final_content else None
        }
        
        if tool_calls:
            # Convert our tool_calls format to the expected format
            formatted_tool_calls = []
            for i, tc in enumerate(tool_calls):
                if tc["function"]["name"]:  # Only add if we have a function name
                    # Ensure we have a valid tool call ID
                    tool_id = tc["id"] if tc["id"] else f"call_{i}_{int(time.time() * 1000)}"
                    
                    formatted_tool_calls.append({
                        "id": tool_id,
                        "type": "function",
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"]
                        }
                    })
            
            if formatted_tool_calls:
                # Important: When there are tool calls, content should be None or empty
                if not final_content:
                    assistant_message["content"] = None
                    
                assistant_message["tool_calls"] = formatted_tool_calls
                conversation_history.append(assistant_message)
                
                # Execute tool calls and add results immediately
                console.print(f"\n[bold #9333ea]⚡ Executing {len(formatted_tool_calls)} function call(s)...[/bold #9333ea]")
                for i, tool_call in enumerate(formatted_tool_calls):
                    console.print(f"[#f472b6]→ {tool_call['function']['name']}[/#f472b6]")
                    
                    try:
                        result = execute_function_call_dict(tool_call, conversation_history)
                        
                        # Check if the result indicates an error
                        if "Error" in result or "error" in result.lower():
                            console.print(f"[bold #ef4444]✗[/bold #ef4444] {result}")
                        else:
                            console.print(f"[bold #10b981]✓[/bold #10b981] {result}")
                        
                        # Add tool result to conversation immediately
                        tool_response = {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": result
                        }
                        conversation_history.append(tool_response)
                    except Exception as e:
                        error_msg = f"Error executing {tool_call['function']['name']}: {e}"
                        console.print(f"[bold #ef4444]✗[/bold #ef4444] {error_msg}")
                        # Still need to add a tool response even on error
                        conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": f"Error: {str(e)}"
                        })
                
                # Get follow-up response after tool execution
                console.print("\n[bold #9333ea]🔄 Processing results...[/bold #9333ea]")
                
                follow_up_stream = client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation_history,
                    tools=tools,
                    max_completion_tokens=2000,
                    stream=True
                )
                
                follow_up_content = ""
                reasoning_started = False
                
                for chunk in follow_up_stream:
                    # Handle reasoning content if available
                    if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                        if not reasoning_started:
                            console.print("\n[bold #c084fc]💭 Reasoning:[/bold #c084fc]")
                            reasoning_started = True
                        console.print(chunk.choices[0].delta.reasoning_content, end="")
                    elif chunk.choices[0].delta.content:
                        if reasoning_started:
                            console.print("\n")
                            console.print("\n[bold #f472b6]🤖 Assistant>[/bold #f472b6] ", end="")
                            reasoning_started = False
                        follow_up_content += chunk.choices[0].delta.content
                        console.print(chunk.choices[0].delta.content, end="")
                
                console.print()
                
                # Store follow-up response
                conversation_history.append({
                    "role": "assistant",
                    "content": follow_up_content
                })
        else:
            # No tool calls, just store the regular response
            conversation_history.append(assistant_message)

        return {"success": True}

    except Exception as e:
        error_msg = f"OpenAI API error: {str(e)}"
        console.print(f"\n[bold #ef4444]❌ {error_msg}[/bold #ef4444]")
        return {"error": error_msg}