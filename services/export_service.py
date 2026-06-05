import csv
import os
from tkinter import filedialog


def export_csv_file(intents_data):
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

        for phrases in intents_data.values():
            for p in phrases:
                writer.writerow([p])