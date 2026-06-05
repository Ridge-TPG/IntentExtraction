import tkinter as tk


def setup_ui(app):
    root = app.root

    # ------------------------
    # TOP TOOLBAR
    # ------------------------
    toolbar = tk.Frame(root)
    toolbar.pack(fill=tk.X, padx=10, pady=5)

    tk.Label(toolbar, text="File:").pack(side=tk.LEFT, padx=5)

    app.file_menu_button = tk.Menubutton(toolbar, text="Open JSON")
    app.file_menu = tk.Menu(app.file_menu_button, tearoff=0)
    app.file_menu_button.config(menu=app.file_menu)

    app.file_menu.add_command(label="Open File...", command=app.open_file)

    app.recent_menu = tk.Menu(app.file_menu, tearoff=0)
    app.file_menu.add_cascade(label="Recent Files", menu=app.recent_menu)

    app.file_menu_button.pack(side=tk.LEFT)

    tk.Label(toolbar, text=" | ").pack(side=tk.LEFT)

    tk.Button(
        toolbar,
        text="Extract",
        command=app.extract_intents,
        bg="#2ECC71",
        fg="white"
    ).pack(side=tk.LEFT, padx=5)

    tk.Label(toolbar, text=" | ").pack(side=tk.LEFT)

    tk.Label(toolbar, text="Output:").pack(side=tk.LEFT, padx=5)

    tk.Button(toolbar, text="Copy", command=app.copy).pack(side=tk.LEFT)
    tk.Button(toolbar, text="Save", command=app.save_markdown).pack(side=tk.LEFT)
    tk.Button(toolbar, text="Clear", command=app.clear_all).pack(side=tk.LEFT)

    tk.Button(toolbar, text="Export CSV", command=app.export_csv).pack(side=tk.RIGHT)

    # ------------------------
    # FILTER BAR
    # ------------------------
    filter_frame = tk.Frame(root)
    filter_frame.pack(fill=tk.X, padx=10)

    tk.Label(filter_frame, text="Filter intents: ").pack(side=tk.LEFT)

    app.filter_entry = tk.Entry(filter_frame)
    app.filter_entry.pack(fill=tk.X, expand=True, padx=5)

    # ------------------------
    # MAIN LAYOUT
    # ------------------------
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # ------------------------
    # LEFT PANEL
    # ------------------------
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    tk.Label(left_frame, text="Intents", font=("Arial", 10, "bold")).pack(anchor="w")

    app.intent_listbox = tk.Listbox(left_frame, height=6)
    app.intent_listbox.pack(fill=tk.X)
    app.intent_listbox.bind("<<ListboxSelect>>", app.on_intent_select)

    tk.Label(left_frame, text="JSON Input", font=("Arial", 11, "bold")).pack(anchor="w")

    input_scroll = tk.Scrollbar(left_frame)
    input_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    app.input_text = tk.Text(
        left_frame,
        yscrollcommand=input_scroll.set,
        state="disabled"
    )
    app.input_text.pack(fill=tk.BOTH, expand=True)

    input_scroll.config(command=app.input_text.yview)

    # ------------------------
    # RIGHT PANEL
    # ------------------------
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    tk.Label(
        right_frame,
        text="Markdown Output",
        font=("Arial", 11, "bold")
    ).pack(anchor="w")

    app.stats_label = tk.Label(right_frame, text="0 intents | 0 phrases")
    app.stats_label.pack(anchor="w")

    output_scroll = tk.Scrollbar(right_frame)
    output_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    app.output_text = tk.Text(
        right_frame,
        yscrollcommand=output_scroll.set,
        state="disabled",
        font=("Consolas", 10)
    )
    app.output_text.pack(fill=tk.BOTH, expand=True)

    output_scroll.config(command=app.output_text.yview)