import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from textblob import TextBlob
import logger

def create_menu(app):
    menu = tk.Menu(app)
    app.config(menu=menu)
    
    # File Menu
    file_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New", command=app.create_default_table)
    file_menu.add_command(label="Open", command=app.open_file)
    file_menu.add_command(label="Save", command=app.save_file)
    file_menu.add_command(label="Save As", command=app.save_file_as)
    file_menu.add_separator()
    file_menu.add_command(label="Close", command=app.close_file)
    file_menu.add_command(label="Exit", command=app.quit)
    
    # Edit Menu
    edit_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Undo", command=app.undo)
    edit_menu.add_command(label="Redo", command=app.redo)
    edit_menu.add_separator()
    edit_menu.add_command(label="Cut", command=lambda: cut(app))
    edit_menu.add_command(label="Copy", command=lambda: copy(app))
    edit_menu.add_command(label="Paste", command=lambda: paste(app))
    edit_menu.add_command(label="Delete", command=lambda: delete(app))
    edit_menu.add_separator()
    edit_menu.add_command(label="Select All", command=lambda: select_all(app))
    
    # View Menu
    view_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="View", menu=view_menu)
    view_menu.add_command(label="Zoom In", command=lambda: zoom_in(app))
    view_menu.add_command(label="Zoom Out", command=lambda: zoom_out(app))
    view_menu.add_command(label="Full Screen", command=lambda: toggle_full_screen(app))
    view_menu.add_separator()
    view_menu.add_command(label="Show Toolbars", command=lambda: show_toolbars(app))
    
    # Insert Menu
    insert_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Insert", menu=insert_menu)
    insert_menu.add_command(label="Insert Image", command=lambda: insert_image(app))
    insert_menu.add_command(label="Insert Table", command=lambda: insert_table(app))
    insert_menu.add_command(label="Insert Chart", command=lambda: insert_chart(app))
    insert_menu.add_command(label="Insert Hyperlink", command=lambda: insert_hyperlink(app))
    
    # Format Menu
    format_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Format", menu=format_menu)
    format_menu.add_command(label="Font", command=lambda: change_font(app))
    format_menu.add_command(label="Paragraph", command=lambda: adjust_paragraph(app))
    format_menu.add_command(label="Style", command=lambda: apply_style(app))
    
    # Tools Menu
    tools_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Tools", menu=tools_menu)
    tools_menu.add_command(label="Spell Check", command=lambda: spell_check(app))
    tools_menu.add_command(label="Word Count", command=lambda: word_count(app))
    tools_menu.add_command(label="Preferences", command=lambda: open_preferences(app))
    
    # Help Menu
    help_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="Help Contents", command=lambda: open_help(app))
    help_menu.add_command(label="About", command=lambda: show_about(app))
    help_menu.add_command(label="Check for Updates", command=lambda: check_updates(app))
    help_menu.add_command(label="Feedback", command=lambda: provide_feedback(app))

def connect_db(app):
    logger.info_logger.info("Connected to XFMEA Database (simulated)")
    messagebox.showinfo("Info", "Connected to XFMEA Database (simulated).")

def cut(app):
    selected_item = app.tree.selection()
    if selected_item:
        app.clipboard_clear()
        app.clipboard_append(" ".join(app.tree.item(selected_item[0])['values']))
        app.tree.delete(selected_item)
        logger.info_logger.info(f"Cut item: {selected_item}")

def copy(app):
    selected_item = app.tree.selection()
    if selected_item:
        app.clipboard_clear()
        app.clipboard_append(" ".join(app.tree.item(selected_item[0])['values']))
        logger.info_logger.info(f"Copied item: {selected_item}")

def paste(app):
    clipboard_data = app.clipboard_get().split()
    table_contents.insert_row(app, clipboard_data, tags=('oddrow',))
    logger.info_logger.info(f"Pasted item: {clipboard_data}")

def delete(app):
    selected_item = app.tree.selection()
    if selected_item:
        app.tree.delete(selected_item)
        logger.info_logger.info(f"Deleted item: {selected_item}")

def select_all(app):
    for item in app.tree.get_children():
        app.tree.selection_add(item)
    logger.info_logger.info("Selected all items")

def zoom_in(app):
    current_font = app.tree.cget("font")
    font_name, font_size = current_font.rsplit(" ", 1)
    font_size = int(font_size) + 2
    new_font = f"{font_name} {font_size}"
    app.tree.configure(font=new_font)
    logger.info_logger.info("Zoomed in")

def zoom_out(app):
    current_font = app.tree.cget("font")
    font_name, font_size = current_font.rsplit(" ", 1)
    font_size = int(font_size) - 2
    new_font = f"{font_name} {font_size}"
    app.tree.configure(font=new_font)
    logger.info_logger.info("Zoomed out")

def toggle_full_screen(app):
    app.attributes("-fullscreen", not app.attributes("-fullscreen"))
    logger.info_logger.info("Toggled full screen")

def show_toolbars(app):
    if hasattr(app, 'toolbar'):
        app.toolbar.pack_forget() if app.toolbar.winfo_ismapped() else app.toolbar.pack(side="top", fill="x")
    logger.info_logger.info("Toggled toolbar visibility")

def insert_image(app):
    file_path = filedialog.askopenfilename(title="Insert Image", filetypes=(("Image Files", "*.png;*.jpg;*.jpeg;*.gif"), ("All Files", "*.*")))
    if file_path:
        messagebox.showinfo("Info", f"Image inserted: {file_path}")
        logger.info_logger.info(f"Inserted image: {file_path}")

def insert_table(app):
    messagebox.showinfo("Info", "Insert Table function is not implemented yet.")
    logger.info_logger.info("Insert Table function called")

def insert_chart(app):
    messagebox.showinfo("Info", "Insert Chart function is not implemented yet.")
    logger.info_logger.info("Insert Chart function called")

def insert_hyperlink(app):
    url = simpledialog.askstring("Insert Hyperlink", "Enter the URL:")
    if url:
        messagebox.showinfo("Info", f"Hyperlink inserted: {url}")
        logger.info_logger.info(f"Inserted hyperlink: {url}")

def change_font(app):
    font = simpledialog.askstring("Change Font", "Enter the font (e.g., Arial 12):")
    if font:
        app.tree.configure(font=font)
        logger.info_logger.info(f"Changed font to: {font}")

def adjust_paragraph(app):
    alignment = simpledialog.askstring("Adjust Paragraph", "Enter the alignment (left, center, right):")
    if alignment:
        messagebox.showinfo("Info", f"Paragraph alignment set to: {alignment}")
        logger.info_logger.info(f"Adjusted paragraph alignment to: {alignment}")

def apply_style(app):
    style = simpledialog.askstring("Apply Style", "Enter the style (e.g., Bold, Italic):")
    if style:
        messagebox.showinfo("Info", f"Style applied: {style}")
        logger.info_logger.info(f"Applied style: {style}")

def spell_check(app):
    text = "\n".join(" ".join(app.tree.item(item)['values']) for item in app.tree.get_children())
    blob = TextBlob(text)
    misspelled = [word for word in blob.words if not word.correct()]
    if misspelled:
        messagebox.showinfo("Spell Check", f"Misspelled words: {', '.join(misspelled)}")
        logger.warning_logger.warning(f"Spell check found misspelled words: {', '.join(misspelled)}")
    else:
        messagebox.showinfo("Spell Check", "No misspellings found.")
        logger.info_logger.info("Spell check found no misspellings")

def word_count(app):
    text = "\n".join(" ".join(app.tree.item(item)['values']) for item in app.tree.get_children())
    blob = TextBlob(text)
    word_count = len(blob.words)
    messagebox.showinfo("Word Count", f"Word count: {word_count}")
    logger.info_logger.info(f"Word count: {word_count}")

def open_preferences(app):
    messagebox.showinfo("Info", "Open Preferences function is not implemented yet.")
    logger.info_logger.info("Open Preferences function called")

def open_help(app):
    messagebox.showinfo("Info", "Open Help function is not implemented yet.")
    logger.info_logger.info("Open Help function called")

def show_about(app):
    messagebox.showinfo("Info", "FMEA Application\nVersion 1.0\n© 2024")
    logger.info_logger.info("Show About function called")

def check_updates(app):
    messagebox.showinfo("Info", "Check for Updates function is not implemented yet.")
    logger.info_logger.info("Check for Updates function called")

def provide_feedback(app):
    feedback = simpledialog.askstring("Provide Feedback", "Enter your feedback:")
    if feedback:
        messagebox.showinfo("Info", "Thank you for your feedback!")
        logger.info_logger.info(f"Feedback received: {feedback}")
