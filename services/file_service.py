import json
import os
from tkinter import filedialog


def open_json_file(path=None):
    if not path:
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not path:
            return None, None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return json.dumps(data, indent=2), path


def save_markdown_file(content):
    folder = "saved-phrases"
    os.makedirs(folder, exist_ok=True)

    path = filedialog.asksaveasfilename(
        initialdir=folder,
        defaultextension=".md",
        filetypes=[("Markdown Files", "*.md")]
    )

    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


def copy_to_clipboard(root, content):
    root.clipboard_clear()
    root.clipboard_append(content)