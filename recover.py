import os
import re
import urllib.parse

def unescape_path(p):
    return urllib.parse.unquote(p).replace('file:///', '').replace('/', '\\')

target_dir = r"c:\Users\Cat\Desktop\New folder (3)\test"
brain_dir = r"C:\Users\Cat\.gemini\antigravity\brain"

# We will read all overview.txt files and look for 'File Path: `file:///...`'
# followed by 'Showing lines X to Y' and then the numbered lines.
files_to_recover = {}

overview_files = []
for root, dirs, files in os.walk(brain_dir):
    if 'overview.txt' in files:
        overview_files.append(os.path.join(root, 'overview.txt'))

overview_files.sort(key=os.path.getmtime) # process oldest to newest so newest overwrites

for overview_path in overview_files:
    with open(overview_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # Split by 'File Path: `'
    blocks = content.split('File Path: `')
    for block in blocks[1:]:
        end_path_idx = block.find('`')
        if end_path_idx == -1: continue
        file_path_url = block[:end_path_idx]
        file_path = unescape_path(file_path_url).lower()
        
        # Only care if it belongs to our target dir
        if not file_path.startswith(target_dir.lower()): continue
        
        # Extract lines
        # Format is <line_number>: <content>
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
            
        # Merge lines (this will keep the latest viewed lines)
        start_line_match = re.search(r'Showing lines (\d+) to (\d+)', block)
        if start_line_match:
            start_line = int(start_line_match.group(1))
            for i, line_content in enumerate(reconstructed):
                files_to_recover[file_path][start_line + i] = line_content

# Now write them out if they are currently 0 bytes
for fp, lines_dict in files_to_recover.items():
    actual_path = None
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            if os.path.join(root, f).lower() == fp.lower():
                actual_path = os.path.join(root, f)
                break
        if actual_path: break
        
    if actual_path and os.path.exists(actual_path) and os.path.getsize(actual_path) == 0:
        print(f"Recovering {actual_path}")
        max_line = max(lines_dict.keys()) if lines_dict else 0
        content_lines = []
        for i in range(1, max_line + 1):
            content_lines.append(lines_dict.get(i, ''))
        
        with open(actual_path, 'w', encoding='utf-8') as out:
            out.write('\n'.join(content_lines))
        
        # apply replacement
        with open(actual_path, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace('EduResult', 'Bhartiya Institute of Professional Studies Ujjain').replace('Edu Result', 'Bhartiya Institute of Professional Studies Ujjain')
        with open(actual_path, 'w', encoding='utf-8') as out:
            out.write(c)

print("Recovery attempted from view logs.")
