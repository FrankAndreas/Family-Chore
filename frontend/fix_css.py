import os

filepath = 'src/pages/user/RewardHub.css'
with open(filepath, 'r') as f:
    css_text = f.read()

lines = css_text.split('\n')
new_lines = []
in_media = False
brace_level = 0

for line in lines:
    if "@media (prefers-color-scheme: dark)" in line:
        in_media = True
        brace_level = line.count('{') - line.count('}')
        continue
        
    if in_media:
        brace_level += line.count('{') - line.count('}')
        if brace_level == 0 and '}' in line:
            in_media = False
            # We don't append the closing brace
            continue
            
        # Un-indent one level if possible
        if line.startswith('    '):
            new_lines.append(line[4:])
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(filepath, 'w') as f:
    f.write('\n'.join(new_lines))

print("done")
