import tkinter as tk
import table_contents

class TableScreen2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        table_contents.create_table(self)
