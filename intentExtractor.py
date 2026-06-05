import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox


class IntentExtractorApp:
    MAX_RECENT = 5

    def __init__(self, root):
        self.root = root
        self.root.title("Intent Extractor Dashboard")
        self.root.geometry("1100x650")

        self.recent_files = []

        self.setup_ui()

    # ------------------------
    # UI SETUP
    # ------------------------
    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=10, pady=5)

        self.file_menu_button = tk.Menubutton(toolbar, text="Open JSON", relief=tk.RAISED)
        self.file_menu = tk.Menu(self.file_menu_button, tearoff=0)
        self.file_menu_button.config(menu=self.file_menu)

        self.file_menu.add_command(label="Open File...", command=self.open_file)

        self.recent_menu = tk.Menu(self.file_menu, tearoff=0)
        self.file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)

        self.file_menu_button.pack(side=tk.LEFT, padx=5)

        tk.Button(toolbar, text="Extract", command=self.extract_intents, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)

        tk.Label(toolbar, text="|").pack(side=tk.LEFT, padx=10)

        tk.Button(toolbar, text="Copy", command=self.copy_to_clipboard).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Save", command=self.save_markdown).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Clear", command=self.clear_all).pack(side=tk.LEFT)

        # Filter
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(fill=tk.X, padx=10)

        tk.Label(filter_frame, text="Filter intents: ").pack(side=tk.LEFT)
        self.filter_entry = tk.Entry(filter_frame)
        self.filter_entry.pack(fill=tk.X, expand=True, padx=5)

        # Main panels
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # LEFT
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(left_frame, text="JSON Input", font=("Arial", 11, "bold")).pack(anchor="w")

        input_scroll = tk.Scrollbar(left_frame)
        input_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.input_text = tk.Text(left_frame, yscrollcommand=input_scroll.set)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        input_scroll.config(command=self.input_text.yview)

        # RIGHT
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(right_frame, text="Markdown Output", font=("Arial", 11, "bold")).pack(anchor="w")

        self.stats_label = tk.Label(right_frame, text="0 intents | 0 phrases")
        self.stats_label.pack(anchor="w")

        output_scroll = tk.Scrollbar(right_frame)
        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.output_text = tk.Text(right_frame, yscrollcommand=output_scroll.set)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        output_scroll.config(command=self.output_text.yview)

    # ------------------------
    # CORE LOGIC
    # ------------------------
    def extract_intents(self):
        try:
            raw = self.input_text.get("1.0", tk.END)
            data = json.loads(raw)

            filter_text = self.filter_entry.get().lower()

            md = "# Extracted Intent Phrases:\n\n"
            intent_count = 0
            phrase_count = 0

            if isinstance(data, dict):
                data = [data]

            for i, item in enumerate(data):

                # Dialogflow
                if isinstance(item, dict) and "trainingPhrases" in item:
                    name = item.get("displayName") or item.get("name") or f"Intent {i+1}"

                    if filter_text and filter_text not in name.lower():
                        continue

                    intent_count += 1
                    md += f"## {name}\n\n**Extracted Intents:**\n\n"

                    for phrase in item.get("trainingPhrases", []):
                        parts = phrase.get("parts", [])
                        full_text = "".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()

                        if full_text:
                            md += f"- {full_text}\n\n"
                            phrase_count += 1

                # Generic
                elif isinstance(item, dict):
                    intents = item.get("intents", [])

                    for intent in intents:
                        name = intent.get("name") or intent.get("intent")

                        if filter_text and filter_text not in name.lower():
                            continue

                        intent_count += 1
                        md += f"## {name}\n\n**Examples:**\n\n"

                        for ex in intent.get("examples", []):
                            md += f"- {ex}\n\n"
                            phrase_count += 1

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, md)

            self.stats_label.config(text=f"{intent_count} intents | {phrase_count} phrases")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ------------------------
    # FILE ACTIONS
    # ------------------------
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, f.read())

        self.add_to_recent(path)

    def save_markdown(self):
        folder = "saved-phrases"
        os.makedirs(folder, exist_ok=True)

        path = filedialog.asksaveasfilename(
            initialdir=folder,
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md")]
        )

        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.output_text.get("1.0", tk.END))

            messagebox.showinfo("Saved", path)

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get("1.0", tk.END))

    def clear_all(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.stats_label.config(text="0 intents | 0 phrases")

    # ------------------------
    # RECENT FILES
    # ------------------------
    def add_to_recent(self, path):
        if path in self.recent_files:
            self.recent_files.remove(path)

        self.recent_files.insert(0, path)

        if len(self.recent_files) > self.MAX_RECENT:
            self.recent_files.pop()

        self.update_recent_menu()

    def update_recent_menu(self):
        self.recent_menu.delete(0, tk.END)

        for path in self.recent_files:
            self.recent_menu.add_command(
                label=os.path.basename(path),
                command=lambda p=path: self.open_recent(p)
            )

    def open_recent(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, f.read())
        except:
            messagebox.showerror("Error", "File not found")


# ------------------------
# RUN APP
# ------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = IntentExtractorApp(root)
    root.mainloop()