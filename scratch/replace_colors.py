import os
import re

file_path = "c:\\Users\\nawad\\OneDrive\\Desktop\\MeusProjetos\\capi_busque\\static\\home\\index.css"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Variables to inject
new_root = """:root {
    --bg-color: #0d1117;
    --accent-color: #58a6ff;
    --text-primary: white;
    --text-secondary: #8b949e;
    --surface-color: #161b22;
    --surface-hover: #21262d;
    --border-color: #30363d;
    --terminal-bg: black;
    --terminal-text: #39ff14;
    --overlay-bg: rgba(0, 0, 0, 0.7);
    --shadow-color: rgba(0,0,0,0.5);
    --accent-shadow: rgba(88, 166, 255, 0.5);
    --icon-dark: #000;
    --icon-light: #fff;
    --danger-color: #ff3333;

    --sidebar-width: 260px;
    --collapsed-width: 70px;
}"""

# Replace ONLY the first :root block which starts at the very beginning
content = re.sub(r"^:root\s*\{.*?\}", new_root, content, count=1, flags=re.DOTALL | re.MULTILINE)

# Replacements list
replacements = [
    ("color: white;", "color: var(--text-primary);"),
    ("background: #161b22;", "background: var(--surface-color);"),
    ("border-right: 1px solid #30363d;", "border-right: 1px solid var(--border-color);"),
    ("background: #21262d;", "background: var(--surface-hover);"),
    ("color: #8b949e;", "color: var(--text-secondary);"),
    ("background: black;", "background: var(--terminal-bg);"),
    ("border: 1px solid #30363d;", "border: 1px solid var(--border-color);"),
    ("color: #39ff14;", "color: var(--terminal-text);"),
    ("background: rgba(0, 0, 0, 0.7);", "background: var(--overlay-bg);"),
    ("border-left: 1px solid #30363d;", "border-left: 1px solid var(--border-color);"),
    ("box-shadow: -10px 0 30px rgba(0,0,0,0.5);", "box-shadow: -10px 0 30px var(--shadow-color);"),
    ("border-bottom: 1px solid #30363d;", "border-bottom: 1px solid var(--border-color);"),
    ("box-shadow: 0 5px 25px rgba(88, 166, 255, 0.5);", "box-shadow: 0 5px 25px var(--accent-shadow);"),
    ("color: #000;", "color: var(--icon-dark);"),
    ("background: #ff3333;", "background: var(--danger-color);"),
    ("color: #fff;", "color: var(--icon-light);")
]

for old, new in replacements:
    content = content.replace(old, new)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Replaced all colors with CSS variables.")
