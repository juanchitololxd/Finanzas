import tkinter as tk

class Test:

    root = tk.Tk()
    menu = tk.Frame()
    panel = tk.Frame()
    def __init__(self):
        pass

    def start(self):
        self.root.mainloop()

    def end(self):
        self.root.destroy()

app = Test()

app.start()
app.end()

