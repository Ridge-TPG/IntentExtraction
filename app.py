from ui.layout import setup_ui
from logic.extractor import extract_intents_logic
from services.file_service import (
    open_json_file, save_markdown_file, copy_to_clipboard
)
from services.export_service import export_csv_file
from utils.helpers import set_text



class IntentExtractorApp:
    MAX_RECENT = 5

    def __init__(self, root):
        self.root = root
        self.root.title("Intent Extractor Dashboard")
        self.root.geometry("1100x650")

        self.recent_files = []
        self.intents_data = {}

        setup_ui(self)  # build UI and attach widgets

    # ------------------------
    # CORE LOGIC
    # ------------------------
    def extract_intents(self):
        raw = self.input_text.get("1.0", "end").strip()
        filter_text = self.filter_entry.get().lower()

        self.intents_data, intent_count, phrase_count = extract_intents_logic(
            raw, filter_text
        )

        # update UI
        self.intent_listbox.delete(0, "end")

        for name, phrases in self.intents_data.items():
            self.intent_listbox.insert("end", f"{name} ({len(phrases)})")

        self.stats_label.config(text=f"{intent_count} intents | {phrase_count} phrases")

        
        if self.intents_data:
            self.intent_listbox.selection_set(0)
            self.intent_listbox.event_generate("<<ListboxSelect>>")


    def on_intent_select(self, event):
        selection = self.intent_listbox.curselection()
        if not selection:
            return

        display_text = self.intent_listbox.get(selection[0])
        name = display_text.rsplit(" (", 1)[0]

        phrases = self.intents_data.get(name, [])

        md = f"# {name}\n\n**Phrases:**\n\n"
        for p in phrases:
            md += f"- {p}\n\n"

        set_text(self.output_text, md)

    # ------------------------
    # FILE ACTIONS
    # ------------------------
    def open_file(self):
        content, path = open_json_file()
        if content:
            set_text(self.input_text, content)
            self.add_to_recent(path)

    def save_markdown(self):
        save_markdown_file(self.output_text.get("1.0", "end"))

    def copy(self):
        copy_to_clipboard(self.root, self.output_text.get("1.0", "end"))

    def export_csv(self):
        export_csv_file(self.intents_data)

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
        self.recent_menu.delete(0, "end")

        for path in self.recent_files:
            self.recent_menu.add_command(
                label=path.split("/")[-1],
                command=lambda p=path: self.open_recent(p)
            )

    def open_recent(self, path):
        content, _ = open_json_file(path)
        if content:
            set_text(self.input_text, content)
    
    def clear_all(self):

        set_text(self.input_text, "")
        set_text(self.output_text, "")
        self.intent_listbox.delete(0, "end")
        self.stats_label.config(text="0 intents | 0 phrases")