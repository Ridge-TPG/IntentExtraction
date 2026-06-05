import json
import os
import csv
import tkinter as tk
from tkinter import filedialog, messagebox


class IntentExtractorApp:
    MAX_RECENT = 5

    def __init__(self, root):
        self.root = root
        self.root.title("Intent Extractor Dashboard")
        self.root.geometry("1100x650")

        self.recent_files = []
        self.intents_data = {}  # NEW: stores intents + phrases

        self.setup_ui()

    # ------------------------
    # UI SETUP
    # ------------------------
    def setup_ui(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(toolbar, text="File:").pack(side=tk.LEFT, padx=5)

        self.file_menu_button = tk.Menubutton(toolbar, text="Open JSON")
        self.file_menu = tk.Menu(self.file_menu_button, tearoff=0)
        self.file_menu_button.config(menu=self.file_menu)

        self.file_menu.add_command(label="Open File...", command=self.open_file)

        self.recent_menu = tk.Menu(self.file_menu, tearoff=0)
        self.file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)

        self.file_menu_button.pack(side=tk.LEFT)

        tk.Label(toolbar, text=" | ").pack(side=tk.LEFT)

        tk.Button(toolbar, text="Extract", command=self.extract_intents,
                  bg="#2ECC71", fg="white").pack(side=tk.LEFT, padx=5)

        tk.Label(toolbar, text=" | ").pack(side=tk.LEFT)

        tk.Label(toolbar, text="Output:").pack(side=tk.LEFT, padx=5)

        tk.Button(toolbar, text="Copy", command=self.copy_to_clipboard).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Save", command=self.save_markdown).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Clear", command=self.clear_all).pack(side=tk.LEFT)

        tk.Button(toolbar, text="Export CSV", command=self.export_csv).pack(side=tk.RIGHT)

        # Filter
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(fill=tk.X, padx=10)

        tk.Label(filter_frame, text="Filter intents: ").pack(side=tk.LEFT)
        self.filter_entry = tk.Entry(filter_frame)
        self.filter_entry.pack(fill=tk.X, expand=True, padx=5)

        # Main layout
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # LEFT PANEL
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Intent list
        tk.Label(left_frame, text="Intents", font=("Arial", 10, "bold")).pack(anchor="w")

        self.intent_listbox = tk.Listbox(left_frame, height=6)
        self.intent_listbox.pack(fill=tk.X)
        self.intent_listbox.bind("<<ListboxSelect>>", self.on_intent_select)

        # JSON input
        tk.Label(left_frame, text="JSON Input", font=("Arial", 11, "bold")).pack(anchor="w")

        input_scroll = tk.Scrollbar(left_frame)
        input_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.input_text = tk.Text(left_frame, yscrollcommand=input_scroll.set, state="disabled")
        self.input_text.pack(fill=tk.BOTH, expand=True)

        input_scroll.config(command=self.input_text.yview)

        # RIGHT PANEL
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(right_frame, text="Markdown Output", font=("Arial", 11, "bold")).pack(anchor="w")

        self.stats_label = tk.Label(right_frame, text="0 intents | 0 phrases")
        self.stats_label.pack(anchor="w")

        output_scroll = tk.Scrollbar(right_frame)
        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.output_text = tk.Text(
            right_frame,
            yscrollcommand=output_scroll.set,
            state="disabled",
            font=("Consolas", 10)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        output_scroll.config(command=self.output_text.yview)

    # ------------------------
    # CORE LOGIC
    # ------------------------
    
    def extract_intents(self):
        self.intents_data.clear()
        self.intent_listbox.delete(0, tk.END)

        raw = self.input_text.get("1.0", tk.END).strip()
        if not raw:
            return

        data = json.loads(raw)
        filter_text = self.filter_entry.get().lower()

        intent_count = 0
        phrase_count = 0

        if isinstance(data, dict):
            data = [data]

        for item in data:

            # ✅ Dialogflow-style
            if isinstance(item, dict) and "trainingPhrases" in item:

                # --- Build phrases FIRST ---
                phrases = []

                for phrase in item.get("trainingPhrases", []):
                    parts = phrase.get("parts", [])
                    full_text = "".join(
                        p.get("text", "") for p in parts if isinstance(p, dict)
                    ).strip()

                    if full_text:
                        # ✅ FILTER BY PHRASE
                        if not filter_text or filter_text in full_text.lower():
                            phrases.append(full_text)
                            phrase_count += 1

                # ✅ Only include intent if phrases matched
                if phrases:

                    name = item.get("displayName") or item.get("name")

                    # ✅ Fallback name
                    if not name:
                        name = phrases[0][:30] + "..." if phrases else f"Intent {intent_count + 1}"

                    self.intents_data[name] = phrases

                    # ✅ Show count in list
                    self.intent_listbox.insert(tk.END, f"{name} ({len(phrases)})")

                    intent_count += 1

            # ✅ Generic schema
            elif isinstance(item, dict):

                for intent in item.get("intents", []):

                    name = intent.get("name") or intent.get("intent")
                    phrases = []

                    for ex in intent.get("examples", []):
                        if isinstance(ex, str):
                            # ✅ FILTER BY PHRASE
                            if not filter_text or filter_text in ex.lower():
                                phrases.append(ex)
                                phrase_count += 1

                    if phrases:
                        self.intents_data[name] = phrases
                        self.intent_listbox.insert(tk.END, f"{name} ({len(phrases)})")
                        intent_count += 1

        self.stats_label.config(text=f"{intent_count} intents | {phrase_count} phrases")

        # ✅ Auto-select first
        if self.intents_data:
            self.intent_listbox.selection_set(0)
            self.intent_listbox.event_generate("<<ListboxSelect>>")


    # ------------------------
    # INTENT VIEW
    # ------------------------

    def on_intent_select(self, event):
        selection = self.intent_listbox.curselection()
        if not selection:
            return

        display_text = self.intent_listbox.get(selection[0])

        # ✅ Remove "(count)"
        name = display_text.rsplit(" (", 1)[0]

        self.show_intent(name)


    def show_intent(self, name):
        phrases = self.intents_data.get(name, [])

        md = f"# {name}\n\n**Phrases:**\n\n"
        for p in phrases:
            md += f"- {p}\n\n"

        self.set_text(self.output_text, md)

    # ------------------------
    # FILE ACTIONS
    # ------------------------
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            pretty = json.dumps(data, indent=2)

        self.set_text(self.input_text, pretty)
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

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get("1.0", tk.END))

    def clear_all(self):
        self.set_text(self.input_text, "")
        self.set_text(self.output_text, "")
        self.intent_listbox.delete(0, tk.END)
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
        with open(path, "r", encoding="utf-8") as f:
            self.set_text(self.input_text, f.read())

    # ------------------------
    # HELPERS
    # ------------------------
    def set_text(self, widget, content):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", content)
        widget.config(state="disabled")

    # ------------------------
    # EXPORT CSV
    # ------------------------
    def export_csv(self):
        folder = "saved-phrases"
        os.makedirs(folder, exist_ok=True)

        path = filedialog.asksaveasfilename(
            initialdir=folder,
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )

        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            for phrases in self.intents_data.values():
                for p in phrases:
                    writer.writerow([p])


# ------------------------
# RUN APP
# ------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = IntentExtractorApp(root)
    root.mainloop()