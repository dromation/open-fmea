import tkinter as tk

class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="Welcome to the FMEA Application")
        label.pack(side="top", fill="x", pady=10)
