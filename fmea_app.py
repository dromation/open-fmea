import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os
import importlib
from PIL import Image, ImageTk
import menu_contents
import table_contents
import data_handler
import logger

class FMEAApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.base_width = 600
        self.base_height = int(self.base_width * 0.75)  # Example ratio (4:3)
        self.geometry(f"{self.base_width}x{self.base_height}")
        self.minsize(self.base_width, self.base_height)

        self.current_file = None
        self.undo_stack = []
        self.redo_stack = []

        # Create a container for the screen manager
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        self.frames = {}
        self.create_top_app_bar()

        self.load_screens(container)
        self.show_frame("HomeScreen")
        menu_contents.create_menu(self)
        self.init_db()

        logger.app_logger.info("FMEA Application initialized")

    def create_top_app_bar(self):
        top_app_bar = tk.Frame(self, bg="lightgrey", height=50)
        top_app_bar.pack(side="top", fill="x")

        # Create buttons with icons
        buttons_info = [
            ("media/topbar/back_arrow.png", self.show_home),
            ("media/topbar/new_file.png", self.open_file),
            ("media/topbar/save.png", self.save_file_as),
            ("media/topbar/undo.png", self.undo),
            ("media/topbar/next.png", self.next_screen),
            ("media/topbar/previous.png", self.previous_screen)]

        for icon_path, command in buttons_info:
            image = Image.open(icon_path)
            image = image.resize((30, 30), Image.ANTIALIAS)
            icon = ImageTk.PhotoImage(image)
            button = tk.Button(top_app_bar, image=icon, command=command)
            button.image = icon  # Keep a reference to avoid garbage collection
            button.pack(side="left", padx=2, pady=2)

    def load_screens(self, container):
        screens_dir = 'screens'
        for filename in os.listdir(screens_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                module = importlib.import_module(f"{screens_dir}.{module_name}")
                class_name = ''.join([part.capitalize() for part in module_name.split('_')])
                screen_class = getattr(module, class_name)
                frame = screen_class(parent=container, controller=self)
                self.frames[class_name] = frame
                frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def show_home(self):
        self.show_frame("HomeScreen")

    def next_screen(self):
        current_frame = self._current_frame()
        next_frame = (current_frame + 1) % len(self.frames)
        frame_name = list(self.frames.keys())[next_frame]
        self.show_frame(frame_name)

    def previous_screen(self):
        current_frame = self._current_frame()
        previous_frame = (current_frame - 1) % len(self.frames)
        frame_name = list(self.frames.keys())[previous_frame]
        self.show_frame(frame_name)

    def _current_frame(self):
        for idx, frame in enumerate(self.frames.values()):
            if frame.winfo_ismapped():
                return idx
        return 0

    def open_file(self):
        filetypes = (("All files", "*.*"), ("Text files", "*.txt"), ("JSON files", "*.json"), ("XML files", "*.xml"), ("SQLite files", "*.sql"))
        filename = filedialog.askopenfilename(title="Open file", filetypes=filetypes)
        if filename:
            try:
                if filename.endswith('.txt'):
                    data = data_handler.load_txt(filename)
                elif filename.endswith('.json'):
                    data = data_handler.load_json(filename)
                elif filename.endswith('.xml'):
                    data = data_handler.load_xml(filename)
                elif filename.endswith('.sql'):
                    data = data_handler.load_sql(filename)
                table_contents.load_data_to_tree(self, data)
                self.current_file = filename  # Set the current file
                logger.info_logger.info(f"File opened: {filename}")
            except Exception as e:
                logger.error_logger.error(f"Failed to open file: {filename}, Error: {e}")

    def save_file(self):
        if self.current_file:
            try:
                data = table_contents.get_table_data(self)
                if self.current_file.endswith('.txt'):
                    data_handler.save_txt(self.current_file, data)
                elif self.current_file.endswith('.json'):
                    data_handler.save_json(self.current_file, data)
                elif self.current_file.endswith('.xml'):
                    data_handler.save_xml(self.current_file, data)
                elif self.current_file.endswith('.sql'):
                    data_handler.save_sql(self.current_file, data)
                logger.info_logger.info(f"File saved: {self.current_file}")
            except Exception as e:
                logger.error_logger.error(f"Failed to save file: {self.current_file}, Error: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        filetypes = (("All files", "*.*"), ("Text files", "*.txt"), ("JSON files", "*.json"), ("XML files", "*.xml"), ("SQLite files", "*.sql"))
        filename = filedialog.asksaveasfilename(title="Save file", filetypes=filetypes, defaultextension=".txt")
        if filename:
            try:
                data = table_contents.get_table_data(self)
                if filename.endswith('.txt'):
                    data_handler.save_txt(filename, data)
                elif filename.endswith('.json'):
                    data_handler.save_json(filename, data)
                elif filename.endswith('.xml'):
                    data_handler.save_xml(filename, data)
                elif filename.endswith('.sql'):
                    data_handler.save_sql(filename, data)
                self.current_file = filename  # Set the current file
                logger.info_logger.info(f"File saved: {filename}")
            except Exception as e:
                logger.error_logger.error(f"Failed to save file: {filename}, Error: {e}")

    def close_file(self):
        self.tree.delete(*self.tree.get_children())
        self.current_file = None  # Clear the current file
        messagebox.showinfo("Info", "File closed successfully.")
        logger.info_logger.info("File closed")

    def undo(self):
        if self.undo_stack:
            last_action = self.undo_stack.pop()
            row_id, column, previous_value = last_action
            self.redo_stack.append((row_id, column, self.tree.set(row_id, column)))
            self.tree.set(row_id, column, previous_value)
            table_contents.update_rpn(self, row_id)
            logger.debug_logger.debug("Undo performed")

    def redo(self):
        if self.redo_stack:
            last_undo = self.redo_stack.pop()
            row_id, column, previous_value = last_undo
            self.undo_stack.append((row_id, column, self.tree.set(row_id, column)))
            self.tree.set(row_id, column, previous_value)
            table_contents.update_rpn(self, row_id)
            logger.debug_logger.debug("Redo performed")

    def connect_db(self):
        menu_contents.connect_db(self)

    def init_db(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS fmea
             (operation_sequence TEXT, part_or_product TEXT, characteristics TEXT, failure_mode TEXT,
              effect_of_failure TEXT, severity INTEGER, classification TEXT, cause_of_failure TEXT, 
              controls_prevention TEXT, occurrence INTEGER, controls_detection TEXT, detection INTEGER, 
              rpn INTEGER, recommended_action TEXT, responsibility TEXT, completion_date TEXT, 
              actions_taken TEXT, severity_a INTEGER, occurrence_a INTEGER, detection_a INTEGER, rpn_a INTEGER)''')
        self.conn.commit()
        logger.info_logger.info("Database initialized")

    def get_data_from_tree(self):
        return table_contents.get_table_data(self)

    def add_sub_row(self, parent_id, values):
        table_contents.insert_row(self, values, tags=self.tree.item(parent_id, "tags"))

    def create_default_table(self):
        default_data = [
            ["1", "Part A", "Characteristic 1", "Failure Mode 1", "Effect 1", "5", "", "Cause 1", "Control 1", "3", "Detection 1", "2", "30", "Action 1", "Person A", "2024-01-01", "Action Taken 1", "4", "2", "2", "16"],
            ["2", "Part B", "Characteristic 2", "Failure Mode 2", "Effect 2", "4", "", "Cause 2", "Control 2", "4", "Detection 2", "3", "48", "Action 2", "Person B", "2024-01-02", "Action Taken 2", "3", "3", "3", "27"]
        ]
        
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(default_data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            row_id = table_contents.insert_row(self, row, tags=(tag,))
            table_contents.update_rpn(self, row_id)
        
        messagebox.showinfo("Info", "Default table created successfully.")
        logger.info_logger.info("Default table created")

    def update_cell(self, row_id, col, value):
        previous_value = self.tree.set(row_id, col)
        self.undo_stack.append((row_id, col, previous_value))
        self.tree.set(row_id, col, value)
        table_contents.update_rpn(self, row_id)
        logger.debug_logger.debug(f"Cell updated: row_id={row_id}, col={col}, value={value}")


if __name__ == "__main__":
    app = FMEAApp()
    app.mainloop()
