import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# recents 
recent_files = []
MAX_RECENT = 5


# ------------------------
# Core Logic
# ------------------------
def extract_intents():
    try:
        raw = input_text.get("1.0", tk.END)
        data = json.loads(raw)

        filter_text = filter_entry.get().lower()

        md = "# Extracted Intent Phrases:\n\n"
        intent_count = 0
        phrase_count = 0

        # Normalize
        if isinstance(data, dict):
            data = [data]

        for item_index, item in enumerate(data):

            # Dialogflow format
            if isinstance(item, dict) and "trainingPhrases" in item:
                name = item.get("displayName") or item.get("name") or f"Intent {item_index+1}"

                if filter_text and filter_text not in name.lower():
                    continue

                intent_count += 1
                md += f"## {name}\n\n"
                md += "**Extracted Intents:**\n\n"

                for phrase in item.get("trainingPhrases", []):
                    parts = phrase.get("parts", [])
                    full_text = ""

                    for part in parts:
                        if isinstance(part, dict):
                            full_text += part.get("text", "")

                    full_text = full_text.strip()

                    if full_text:
                        md += f"- {full_text}\n\n"
                        phrase_count += 1

                md += "\n"

            # Generic format
            elif isinstance(item, dict):
                intents = item.get("intents")

                if intents is None:
                    continue

                for i, intent in enumerate(intents):
                    name = intent.get("name") or intent.get("intent") or f"Intent {i+1}"

                    if filter_text and filter_text not in name.lower():
                        continue

                    intent_count += 1
                    md += f"## {name}\n\n"

                    examples = intent.get("examples") or intent.get("utterances") or []

                    if examples:
                        md += "**Examples:**\n\n"

                        for ex in examples:
                            if isinstance(ex, str):
                                md += f"- {ex}\n\n"
                            elif isinstance(ex, dict):
                                md += f"- {ex.get('text', str(ex))}\n\n"
                                phrase_count += 1

                        md += "\n"

        # Output
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, md)

        # ✅ Update stats
        stats_label.config(text=f"{intent_count} intents | {phrase_count} phrases")

    except Exception as e:
        messagebox.showerror("Error", f"Invalid JSON\n\n{e}")


# ------------------------
# File Actions
# ------------------------
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])

    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            input_text.delete("1.0", tk.END)
            input_text.insert(tk.END, f.read())

        add_to_recent(file_path)

def add_to_recent(file_path):
    if file_path in recent_files:
        recent_files.remove(file_path)

    recent_files.insert(0, file_path)

    if len(recent_files) > MAX_RECENT:
        recent_files.pop()

    update_recent_menu()


def open_recent(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            input_text.delete("1.0", tk.END)
            input_text.insert(tk.END, f.read())
    except:
        messagebox.showerror("Error", "File not found or inaccessible")


def update_recent_menu():
    recent_menu.delete(0, tk.END)

    if not recent_files:
        recent_menu.add_command(label="No recent files", state="disabled")
        return

    for path in recent_files:
        recent_menu.add_command(
            label=path,
            command=lambda p=path: open_recent(p)
        )


def save_markdown():
    folder_name = "saved-phrases"

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    file_path = filedialog.asksaveasfilename(
        initialdir=folder_name,
        defaultextension=".md",
        filetypes=[("Markdown Files", "*.md")]
    )

    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(output_text.get("1.0", tk.END))

        messagebox.showinfo("Saved", f"Saved\n{file_path}")


def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(output_text.get("1.0", tk.END))
    messagebox.showinfo("Copied", "Copied to clipboard")


def clear_all():
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)
    stats_label.config(text="0 intents | 0 phrases")


# ------------------------
# UI Setup
# ------------------------
root = tk.Tk()
root.title("Intent Extractor Dashboard")
root.geometry("1100x650")

# ------------------------
# Top Toolbar
# ------------------------
toolbar = tk.Frame(root)
toolbar.pack(fill=tk.X, padx=10, pady=5)

file_menu_button = tk.Menubutton(toolbar, text="Open JSON", relief=tk.RAISED)
file_menu = tk.Menu(file_menu_button, tearoff=0)
file_menu_button.config(menu=file_menu)

file_menu.add_command(label="Open File...", command=open_file)

# Recent submenu
recent_menu = tk.Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Recent Files", menu=recent_menu)

file_menu_button.pack(side=tk.LEFT, padx=5)
tk.Button(toolbar, text="Extract", command=extract_intents, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)

tk.Label(toolbar, text="|").pack(side=tk.LEFT, padx=10)

tk.Button(toolbar, text="Copy", command=copy_to_clipboard).pack(side=tk.LEFT, padx=5)
tk.Button(toolbar, text="Save", command=save_markdown).pack(side=tk.LEFT, padx=5)
tk.Button(toolbar, text="Clear", command=clear_all).pack(side=tk.LEFT, padx=5)

# ------------------------
# Filter Bar
# ------------------------
filter_frame = tk.Frame(root)
filter_frame.pack(fill=tk.X, padx=10)

tk.Label(filter_frame, text="Filter intents: ").pack(side=tk.LEFT)

filter_entry = tk.Entry(filter_frame)
filter_entry.pack(fill=tk.X, expand=True, padx=5)

# ------------------------
# Main Panels
# ------------------------
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# LEFT (Input)
left_frame = tk.Frame(main_frame)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

tk.Label(left_frame, text="JSON Input", font=("Arial", 11, "bold")).pack(anchor="w")

input_scroll = tk.Scrollbar(left_frame)
input_scroll.pack(side=tk.RIGHT, fill=tk.Y)

input_text = tk.Text(left_frame, yscrollcommand=input_scroll.set)
input_text.pack(fill=tk.BOTH, expand=True)

input_scroll.config(command=input_text.yview)

# RIGHT (Output)
right_frame = tk.Frame(main_frame)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

tk.Label(right_frame, text="Markdown Output", font=("Arial", 11, "bold")).pack(anchor="w")

# Stats panel
stats_label = tk.Label(right_frame, text="0 intents | 0 phrases")
stats_label.pack(anchor="w")

output_scroll = tk.Scrollbar(right_frame)
output_scroll.pack(side=tk.RIGHT, fill=tk.Y)

output_text = tk.Text(right_frame, yscrollcommand=output_scroll.set)
output_text.pack(fill=tk.BOTH, expand=True)

output_scroll.config(command=output_text.yview)

# Run
root.mainloop()