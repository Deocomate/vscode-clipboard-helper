import os
import mimetypes

def is_text_file(filepath: str) -> bool:
    """
    Check if a file is a text file.
    Uses mimetypes database and falls back to checking common text extensions.
    """
    if not os.path.isfile(filepath):
        return False
        
    type_mime, _ = mimetypes.guess_type(filepath)
    if type_mime and type_mime.startswith('text/'):
        return True
        
    text_extensions = {
        '.py', '.js', '.ts', '.html', '.css', '.txt', '.md', '.json',
        '.xml', '.yml', '.yaml', '.sh', '.bat', '.csv', '.ini', '.cfg',
        '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.php', '.rb',
        '.jsx', '.tsx', '.vue', '.svelte', '.sql', '.toml'
    }
    
    ext = os.path.splitext(filepath)[1].lower()
    return ext in text_extensions

def merge_files_to_text(file_list: list[str]) -> str:
    """
    Reads text files and merges into a single string formatted like:
    --- File name ---
    [content]
    """
    merged_lines = []
    
    for filepath in file_list:
        if not os.path.isfile(filepath):
            continue
            
        if is_text_file(filepath):
            filename = os.path.basename(filepath)
            merged_lines.append(f"--- {filename} ---")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    merged_lines.append(f.read())
            except Exception as e:
                merged_lines.append(f"[Error reading file: {e}]")
            merged_lines.append("") # Empty line between files
            
    return "\n".join(merged_lines)
