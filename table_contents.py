import tkinter as tk
from tkinter import ttk

def create_table(app):
    columns = [
        "Operation Sequence", "Part or Product", "Characteristics", "Failure Mode", 
        "Effect of Failure", "Severity", "Classification", "Cause of Failure", 
        "Controls Prevention", "Occurrence", "Controls Detection", "Detection", 
        "RPN", "Recommended Action", "Responsibility", "Completion Date", 
        "Actions Taken", "Severity A", "Occurrence A", "Detection A", "RPN A"
    ]
    
    app.tree = ttk.Treeview(app, columns=columns, show='headings')
    app.tree.pack(expand=True, fill='both')
    
    for col in columns:
        app.tree.heading(col, text=col)
        app.tree.column(col, anchor='w', width=120)

    app.tree.tag_configure('oddrow', background='white')
    app.tree.tag_configure('evenrow', background='lightgray')
    app.tree.tag_configure('rpn_low', background='green')
    app.tree.tag_configure('rpn_medium', background='yellow')
    app.tree.tag_configure('rpn_high', background='red')

    app.entry = None  # This will hold the Entry widget for editing cells
    app.combo = None  # This will hold the Combobox widget for specific columns
    app.tree.bind('<Double-1>', lambda event: edit_cell(app, event))

    add_scrollbars(app)

def add_scrollbars(app):
    vsb = ttk.Scrollbar(app, orient="vertical", command=app.tree.yview)
    vsb.pack(side='right', fill='y')
    app.tree.configure(yscrollcommand=vsb.set)

    hsb = ttk.Scrollbar(app, orient="horizontal", command=app.tree.xview)
    hsb.pack(side='bottom', fill='x')
    app.tree.configure(xscrollcommand=hsb.set)

def insert_row(app, values=None, tags=()):
    values = values or [""] * len(app.tree["columns"])
    row_id = app.tree.insert('', 'end', values=values, tags=tags)
    update_rpn(app, row_id)
    return row_id

def get_table_data(app):
    data = []
    for row_id in app.tree.get_children():
        row = []
        for col in app.tree["columns"]:
            row.append(app.tree.set(row_id, col))
        data.append(row)
    return data

def load_data_to_tree(app, data):
    app.tree.delete(*app.tree.get_children())
    for i, row in enumerate(data):
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        row_id = insert_row(app, row, tags=(tag,))
        update_rpn(app, row_id)

def edit_cell(app, event):
    region = app.tree.identify("region", event.x, event.y)
    if region != "cell":
        return

    row_id = app.tree.identify_row(event.y)
    column = app.tree.identify_column(event.x)
    col_num = int(column[1:]) - 1

    x, y, width, height = app.tree.bbox(row_id, column)
    value = app.tree.set(row_id, column)

    specific_columns = ["Severity", "Occurrence", "Detection", "Severity A", "Occurrence A", "Detection A"]

    if app.tree.heading(column)['text'] in specific_columns:
        app.combo = ttk.Combobox(app, values=[str(i) for i in range(1, 11)], state='readonly')
        app.combo.place(x=x, y=y, width=width, height=height)
        app.combo.set(value)
        app.combo.focus()

        def save_edit(event):
            previous_value = app.tree.set(row_id, column)
            app.tree.set(row_id, column, app.combo.get())
            app.combo.destroy()
            app.combo = None
            app.undo_stack.append((row_id, column, previous_value))
            update_rpn(app, row_id)

        app.combo.bind('<<ComboboxSelected>>', save_edit)
        app.combo.bind('<FocusOut>', save_edit)
    else:
        app.entry = tk.Entry(app, width=width)
        app.entry.place(x=x, y=y, width=width, height=height)
        app.entry.insert(0, value)
        app.entry.focus()

        def save_edit(event):
            previous_value = app.tree.set(row_id, column)
            app.tree.set(row_id, column, app.entry.get())
            app.entry.destroy()
            app.entry = None
            app.undo_stack.append((row_id, column, previous_value))
            update_rpn(app, row_id)

        app.entry.bind('<Return>', save_edit)
        app.entry.bind('<FocusOut>', save_edit)

def update_rpn(app, row_id):
    def get_rpn_color_tag(value):
        if value <= 20:
            return 'rpn_low'
        elif value <= 45:
            return 'rpn_medium'
        else:
            return 'rpn_high'

    try:
        severity = int(app.tree.set(row_id, "Severity"))
        occurrence = int(app.tree.set(row_id, "Occurrence"))
        detection = int(app.tree.set(row_id, "Detection"))
        rpn = severity * occurrence * detection
        app.tree.set(row_id, "RPN", rpn)
        color_tag = get_rpn_color_tag(rpn)
        tags = list(app.tree.item(row_id, 'tags'))
        tags = [t for t in tags if not t.startswith('rpn_')]  # Remove old rpn tags
        tags.append(color_tag)
        app.tree.item(row_id, tags=tuple(tags))
        app.tree.tag_configure('rpn_low', background='green')
        app.tree.tag_configure('rpn_medium', background='yellow')
        app.tree.tag_configure('rpn_high', background='red')
    except ValueError:
        app.tree.set(row_id, "RPN", "")
        tags = list(app.tree.item(row_id, 'tags'))
        tags = [t for t in tags if not t.startswith('rpn_')]
        app.tree.item(row_id, tags=tuple(tags))

    try:
        severity_a = int(app.tree.set(row_id, "Severity A"))
        occurrence_a = int(app.tree.set(row_id, "Occurrence A"))
        detection_a = int(app.tree.set(row_id, "Detection A"))
        rpn_a = severity_a * occurrence_a * detection_a
        app.tree.set(row_id, "RPN A", rpn_a)
        color_tag_a = get_rpn_color_tag(rpn_a)
        tags = list(app.tree.item(row_id, 'tags'))
        tags = [t for t in tags if not t.startswith('rpn_')]
        tags.append(color_tag_a)
        app.tree.item(row_id, tags=tuple(tags))
        app.tree.tag_configure('rpn_low', background='green')
        app.tree.tag_configure('rpn_medium', background='yellow')
        app.tree.tag_configure('rpn_high', background='red')
    except ValueError:
        app.tree.set(row_id, "RPN A", "")
        tags = list(app.tree.item(row_id, 'tags'))
        tags = [t for t in tags if not t.startswith('rpn_')]
        app.tree.item(row_id, tags=tuple(tags))

