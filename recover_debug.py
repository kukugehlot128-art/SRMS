import os
import re
import urllib.parse

def unescape_path(p):
    return urllib.parse.unquote(p).replace('file:///', '').replace('/', '\\')

target_dir = r"c:\Users\Cat\Desktop\New folder (3)\test"
brain_dir = r"C:\Users\Cat\.gemini\antigravity\brain"

overview_files = []
for root, dirs, files in os.walk(brain_dir):
    if 'overview.txt' in files:
        overview_files.append(os.path.join(root, 'overview.txt'))

print(f"Found {len(overview_files)} overview.txt files")

files_to_recover = {}

for overview_path in sorted(overview_files, key=os.path.getmtime):
    with open(overview_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    blocks = content.split('File Path: `')
    for block in blocks[1:]:
        end_path_idx = block.find('`')
        if end_path_idx == -1: continue
        file_path_url = block[:end_path_idx]
        file_path = unescape_path(file_path_url).lower()
        
        if not file_path.startswith(target_dir.lower()): continue
        
        lines_text_start = block.find('The following code has been modified')
        if lines_text_start == -1: continue
        lines_text_start = block.find('\n', lines_text_start) + 1
        
        lines_text_end = block.find('\nThe above content does NOT show', lines_text_start)
        if lines_text_end == -1:
            lines_text_end = block.find('\nThe above content shows the entire', lines_text_start)
        if lines_text_end == -1:
            continue
            
        lines_block = block[lines_text_start:lines_text_end]
        
        reconstructed = []
        for line in lines_block.split('\n'):
            idx = line.find(': ')
            if idx != -1 and line[:idx].isdigit():
                reconstructed.append(line[idx+2:])
        
        if file_path not in files_to_recover:
            files_to_recover[file_path] = {}
            
        start_line_match = re.search(r'Showing lines (\d+) to (\d+)', block)
        if start_line_match:
            start_line = int(start_line_match.group(1))
            for i, line_content in enumerate(reconstructed):
                files_to_recover[file_path][start_line + i] = line_content

print(f"Found {len(files_to_recover)} files in logs.")
for k, v in files_to_recover.items():
    print(k, len(v), "lines")

