from Shared import *
from Panel import Panel
from Tabla import TablaCompras, TablaCategorias


class App:
    """
    Aplicación de finanzas GUI.
    """
    menuItems = ['Summary', 'Ingresos', 'Egresos', 'WishList']

    def __init__(self):
        self.menu = tk.Frame(master=app)
        self.panel = tk.Frame(master=app)
        self.tablas = tk.Frame(master=app)
        self.footer = tk.Frame(master=app)
        app.geometry("{0}x{1}+0+0".format(
            app.winfo_screenwidth() + 3, app.winfo_screenheight() + 3))
        app.title("FinanzasJP")
        self.menu.config(bg=color)
        self.menu.pack(side=tk.LEFT, fill=tk.Y)
        self.panel.pack(pady=20)
        self.tablas.pack(fill=tk.X, pady=20)
        self.footer.pack(pady=20)

    def start(self):
        self.generateMenu()
        self.generateContent()
        app.mainloop()

    def generateMenu(self):
        """Genera el menu lateral izquierdo
        """
        for submenu in self.menuItems:
            item = tk.Menubutton(master=self.menu, text=submenu)
            item.pack(pady="6", fill="x")
            item.config(bg="#B8A5A1")

    def generateContent(self):
        """
        Genera el contenido principal (panel y las tablas)
        :return:
        """
        Panel(self.panel)
        TablaCompras(Finanzas.getGastos(), self.tablas).getTable().pack(side=tk.LEFT, padx=150)
        TablaCategorias(Finanzas.getCategoriesAndVF(), self.tablas).getTable().pack(
            side=tk.RIGHT, padx=150)
        tk.Button(master=self.footer, text="GUARDAR", command=App.saveChanges).pack(side=tk.LEFT, padx=20)
        tk.Button(master=self.footer, text="DESCARTAR", command=App.discardChanges).pack(side=tk.RIGHT, padx=20)
        self.entry = tk.Entry(master=self.footer)
        self.entry.pack()
        tk.Button(master=self.footer, text="Subir", command=self.exec).pack(padx=20)

    def exec(self):
        Finanzas.execQueryNoSelect(self.entry.get())

    @staticmethod
    def saveChanges():
        Finanzas.saveChanges("Y")

    @staticmethod
    def discardChanges():
        Finanzas.saveChanges("N")

    @staticmethod
    def end():
        """
        Termina la ejecución de la GUI y de la conexión
        :return:
        """
        Finanzas.saveChanges("y")
        Finanzas.close()
        try:
            app.destroy()
        except:
            pass


def main():
    a = App()
    a.start()
    a.end()


main()
