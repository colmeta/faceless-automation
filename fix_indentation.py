import os

def fix_indentation():
    file_path = 'master_automation.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Target line index (0-based)
    # Line 696 in 1-based is index 695
    # We want to check if line 695 is indeed the 'if background is None:' check
    
    start_index = -1
    for i, line in enumerate(lines):
        if "if background is None:" in line and "STEP 3" in lines[i-1]:
            start_index = i
            print(f"Found start at line {i+1}: {line.strip()}")
            break
    
    if start_index == -1:
        print("Could not find the target block.")
        return

    # We need to indent from start_index + 1 until we hit "STEP 4"
    end_index = -1
    for i in range(start_index + 1, len(lines)):
        if "STEP 4: Add hook text" in lines[i]:
            if "STEP 4: Add hook text" in lines[i]:
                end_index = i
                print(f"Found end at line {i+1}: {lines[i].strip()}")
                break
    
    if end_index == -1:
        print("Could not find the end of the block.")
        return

    # Apply indentation
    print(f"Indenting lines {start_index+2} to {end_index}...")
    for i in range(start_index + 1, end_index):
        if lines[i].strip(): # Only indent non-empty lines
            lines[i] = "    " + lines[i]
        # Empty lines inside the block should probably also be indented or left empty? 
        # Usually left empty is fine, but for consistency let's just indent everything that isn't just a newline
        # Actually, if it's just \n, adding spaces makes it 4 spaces + \n. 
        # Let's only indent if it has content.
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("Indentation fixed.")

if __name__ == "__main__":
    fix_indentation()
