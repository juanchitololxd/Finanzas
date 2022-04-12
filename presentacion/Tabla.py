from Shared import *
from tkinter import ttk

from presentacion.PopUp import PopUpGasto


class Tabla:
    """
    Componente que genera una tabla con su titulo y sus botones
    """

    def __init__(self, data, root):
        self.root = root
        self.cuadro = tk.Frame(master=self.root)
        self.font = ('Helvetica', '18', 'bold')
        self.item = {}
        columns = data['titles']
        self.tree = ttk.Treeview(self.cuadro, columns=columns, show='headings')
        i = 0
        for i in range(len(columns)):
            self.tree.column(columns[i], width=data['widths'][i], anchor='c')
            self.tree.heading(columns[i], text=columns[i])
        self.cargarInfo(data['data'])

        self.generateTitle()
        self.tree.pack()
        self.generateButtons()

    def cargarInfo(self, data):
        #self.tree.delete(self.tree.children)
        for item in data:
            self.tree.insert('', tk.END, values=item)

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
    def __init__(self, data, root):
        super().__init__(data, root)
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
        Finanzas.resetGastosMensuales()

    def agregar(self):
        popup = PopUpGasto(app)

    def pagar(self):
        self.selectItem()
        Finanzas.execProcedure("aplazarCompra", ["'" + self.item['values'][0] + "'"])
        pass

    def aplazar(self):
        self.selectItem()
        Finanzas.execProcedure("itemComprado", ["'" + self.item['values'][0] + "'"])

    def selectItem(self, ah=None):
        curItem = self.tree.focus()
        self.item = self.tree.item(curItem)


class TablaCategorias(Tabla):
    def __init__(self, data, root):
        super().__init__(data, root)

    def generateTitle(self):
        tk.Label(self.cuadro, text="CATEGORIAS", font=self.font).pack(side=tk.TOP)

    def generateButtons(self):
        buttons = tk.Frame(self.cuadro)
        buttons.pack(side=tk.BOTTOM)
        tk.Button(master=buttons, text="Agregar").pack()

"""class TablaDeudas(Tabla):
    def __init__(self, data, root):
        super().__init__(data, root)

    def generateTitle(self):
        tk.Label(self.cuadro, text="DEUDAS", font=self.font).pack(side=tk.TOP)

    def generateButtons(self):
        buttons = tk.Frame(self.cuadro)
        buttons.pack(side=tk.BOTTOM)
        tk.Button(master=buttons, text="Pagar").pack()
    """