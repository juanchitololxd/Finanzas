from Shared import *
from tkinter import ttk

from presentacion.PopUp import PopUpGasto


class Tabla:
    """
    Componente que genera una tabla con su titulo y sus botones
    """

    def __init__(self, data, root, widths):
        self.root = root
        self.cuadro = tk.Frame(master=self.root)
        self.data = data
        self.font = ('Helvetica', '18', 'bold')
        self.item = {}
        columns = []
        for item in data:
            columns += [item]
        self.tree = ttk.Treeview(self.cuadro, columns=columns, show='headings')
        i = 0
        for item in columns:
            self.tree.column(item, width=widths[i], anchor='c')
            self.tree.heading(item, text=item)
            i += 1

        for i in range(len(data[columns[0]].keys())):
            self.tree.insert('', tk.END, values=self.generateArr(columns, i))
        self.generateTitle()
        self.tree.pack()
        self.generateButtons()

    def generateTitle(self):
        pass

    def generateButtons(self):
        pass

    def getTable(self):
        return self.cuadro

    def generateArr(self, columns, i):
        rta = []
        for col in columns:
            rta += [self.data[col][i]]
        return rta


class TablaCompras(Tabla):
    def __init__(self, data, root, widths):
        super().__init__(data, root, widths)
        self.tree.bind('<ButtonRelease-1>', self.selectItem)

    def generateTitle(self):
        tk.Label(self.cuadro, text="GASTOS PENDIENTES", font=self.font).pack(side=tk.TOP)

    def generateButtons(self):
        buttons = tk.Frame(self.cuadro)
        buttons.pack(side=tk.BOTTOM)
        tk.Button(buttons, text="Pagar", command=self.pagar, cursor="hand2").pack(padx=10, pady=10, side=tk.LEFT)
        tk.Button(buttons, text="Aplazar", command=self.aplazar, cursor="hand2").pack(padx=10, pady=10, side=tk.RIGHT)
        tk.Button(buttons, text="Resetear", command=TablaCompras.setGastosMensuales, cursor="hand2")\
            .pack(padx=10, pady=10, side=tk.RIGHT)
        tk.Button(buttons, text="Agregar", command=self.agregar, cursor="hand2").pack(padx=10, pady=10, side=tk.RIGHT)

    @staticmethod
    def setGastosMensuales():
        Finanzas.execOtherSql("UPDATE COMPRAS SET PAGADO = 0")

    def agregar(self):
        popup = PopUpGasto(app)

    def pagar(self):
        self.selectItem()
        Finanzas.execProcedure("aplazarCompra", self.item['values'][0])
        pass

    def aplazar(self):
        self.selectItem()
        Finanzas.execProcedure("itemComprado", self.item['values'][0])

    def selectItem(self, ah=None):
        curItem = self.tree.focus()
        self.item = self.tree.item(curItem)


class TablaCategorias(Tabla):
    def __init__(self, data, root, widths):
        super().__init__(data, root, widths)

    def generateTitle(self):
        tk.Label(self.cuadro, text="CATEGORIAS", font=self.font).pack(side=tk.TOP)

    def generateButtons(self):
        buttons = tk.Frame(self.cuadro)
        buttons.pack(side=tk.BOTTOM)
        tk.Button(master=buttons, text="Agregar").pack()
