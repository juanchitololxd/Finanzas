import tkinter as tk
from tkinter import Canvas, ttk, Toplevel
from connection import Finanzas


class App:
    """
    Aplicación de finanzas GUI.
    """
    root = tk.Tk()
    menu = tk.Frame()
    panel = tk.Frame()
    menuItems = ['Summary', 'Ingresos', 'Egresos', 'WishList']
    color = "#B8A5A1"

    def __init__(self):
        self.root.geometry("{0}x{1}+0+0".format(
            self.root.winfo_screenwidth()+3, self.root.winfo_screenheight()+3))
        self.root.title("FinanzasJP")
        self.menu.config(bg=self.color)
        self.menu.pack(side=tk.LEFT, fill="y")
        self.panel.pack()

    def start(self):
        self.generateMenu()
        self.generateContent()
        self.root.mainloop()

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
        TablaCompras(Finanzas.getGastos(), [100, 100, 100]).getTable().pack(side=tk.LEFT, padx=140)
        TablaCategorias(Finanzas.getCategoriesAndVF(), [100, 100, 100]).getTable().pack(side=tk.RIGHT, padx=140)
        tk.Button(master=self.root, text="Resetear compras mensuales",
                  command=Finanzas.setGastosMensuales).pack(side=tk.BOTTOM)

    def end(self):
        """
        Termina la ejecución de la GUI y de la conexión
        :return:
        """
        Finanzas.close()
        #self.root.destroy()



class CuadroInfo:
    """
    Componente del panel principal que muestra información
    :parameter

    """
    w = 150
    h = 50

    def __init__(self, title, content, root, rigth, coordStart=(0, 0)):
        self.canvas = Canvas(root, height=self.h, width=self.w)
        self.canvas.create_text(coordStart[0], coordStart[1], text=title, fill='green')
        self.canvas.create_text(coordStart[0], coordStart[1] + 20, text=content, fill='green',
                           font=('Helvetica', '15', 'bold'))
        self.selectFunction(title)
        if rigth:
            self.canvas.pack(side=tk.RIGHT)
        else:
            self.canvas.pack(side=tk.LEFT)

    def check_hand(self, e):  # runs on mouse motion
        self.canvas.config(cursor="hand2")

    def selectFunction(self, title):
        self.canvas.bind("<Motion>", self.check_hand)
        if title.upper() == "MES":
            self.canvas.bind("<Button-1>", Panel.setMes)
        elif title.upper() == "INGRESOS":
            self.canvas.bind("<Button-1>", Panel.getIngresos)
        elif title.upper() == "EGRESOS":
            self.canvas.bind("<Button-1>", Panel.getEgresos)
        elif title.upper() == "REPARTIBLE":
            self.canvas.bind("<Button-1>", Panel.repartir)
        elif title.upper() == "TOTAL":
            self.canvas.bind("<Button-1>", Panel.getTotal)
        else:
            self.canvas.bind("<Button-1>", Panel.getDeudas)


class Panel:
    """
    Panel que muestra un resumen de estadísticas
    """
    def __init__(self, root):
        self.filaInf = tk.Frame(master=root)
        self.filaSup = tk.Frame(master=root)
        # Borrar function
        i = 0
        self.items = {
            'Mes': {'content': Panel.getMes()},
            'Ingresos': {'content': Panel.info()},
            'Egresos': {'content': Panel.info()},
            'Repartible': {'content': Panel.info()},
            'Total': {'content': Panel.info()},
            'Deudas': {'content': Panel.info()}
        }

        for item in self.items.keys():
            if i < 3:
                self.appendFila(self.filaInf, item, i)
            else:
                self.appendFila(self.filaSup, item, i)
            i += 1

        self.filaSup.pack(side=tk.TOP)
        self.filaInf.pack(side=tk.BOTTOM)

    def appendFila(self, fila, item, i):
        if i % 2 == 0:
            CuadroInfo(item, self.items[item]["content"], fila, True, (CuadroInfo.w / 2, 10))
        else:
            CuadroInfo(item, self.items[item]["content"], fila, True, (CuadroInfo.w / 2, 10))

    @staticmethod
    def info():
        return "sin terminar"

    @staticmethod
    def repartir(event):
        Finanzas.repartirDinero()

    @staticmethod
    def getMes():
        return Finanzas.getMonth(Finanzas.hoy.month)

    @staticmethod
    def setMes(e):
        pass

    @staticmethod
    def getIngresos(event):
        PopUpIngreso(App.root)

    @staticmethod
    def getEgresos(clas):
        PopUpEgreso(App.root)

    @staticmethod
    def getTotal(cls):
        print("total")

    @staticmethod
    def getDeudas(cls):
        print("deudas")


class Tabla:
    """
    Componente que genera una tabla con su titulo y sus botones
    """
    def __init__(self, data, widths):
        self.root = tk.Frame()
        self.data = data
        self.font = ('Helvetica', '18', 'bold')
        self.item = {}
        columns = []
        for item in data:
            columns += [item]

        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
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
        return self.root

    def generateArr(self, columns, i):
        rta = []
        for col in columns:
            rta += [self.data[col][i]]
        return rta


class TablaCompras(Tabla):
    def __init__(self, data, widths):
        super().__init__(data, widths)
        self.tree.bind('<ButtonRelease-1>', self.selectItem)

    def generateTitle(self):
        tk.Label(self.root, text="GASTOS PENDIENTES", font=self.font).pack(side=tk.TOP)

    def generateButtons(self):
        buttons = tk.Frame(self.root)
        buttons.pack(side=tk.BOTTOM)
        tk.Button(buttons, text="Pagar", command=self.pagar,cursor="hand2").pack(padx=20, pady=10,side=tk.LEFT)
        tk.Button(buttons, text="Aplazar", command=self.aplazar, cursor="hand2").pack(padx=20,pady=10, side=tk.RIGHT)

    def pagar(self):
        pass

    def aplazar(self):
        pass

    def selectItem(self, ah):
        curItem = self.tree.focus()
        self.item = self.tree.item(curItem)
        print(self.tree.item(curItem))


class TablaCategorias(Tabla):
    def __init__(self, data, widths):
        super().__init__(data, widths)

    def generateTitle(self):
        tk.Label(self.root, text="CATEGORIAS", font=self.font).pack(side=tk.TOP)

    def generateButtons(self):
        pass


class PopUp:
    """
    Ventana que puede ser una entrada o salida
    """
    def __init__(self, root):
        self.root = Toplevel(root)
        self.root.geometry("{0}x{1}+{2}+{3}".format(
            round(self.root.winfo_screenwidth()/2), round(self.root.winfo_screenheight()/2),
            round(self.root.winfo_screenwidth()/4), round(self.root.winfo_screenheight()/4)))
        lValue = tk.Label(master=self.root, text="Valor")
        lValue.pack(pady="4")
        self.eValue = tk.Entry(master=self.root, justify="center", width="16")
        self.eValue.configure(font=("Courier", 11))
        self.eValue.pack()
        self.cargueCampos()
        self.cargueBoton()

    def cargueCampos(self):
        pass

    def cargueBoton(self):
        pass


class PopUpIngreso(PopUp):
    entradas = None

    def __init__(self, root):
        super().__init__(root)

    def cargueCampos(self):
        self.entradas = ttk.Combobox(master=self.root, state="readonly")
        opcionesEntrada = Finanzas.getCategories().to_dict()
        aux = []
        for i in range(len(opcionesEntrada["CAT"])):
            aux.append(str(opcionesEntrada["CAT"][i]))
        self.entradas['values'] = aux
        # self.entradas.set("REPARTIR")
        self.entradas.pack(padx="20", pady="6")

    def cargueBoton(self):
        tk.Button(master=self.root, text="Subir",
                  command=Finanzas.insertEntrada(self.eValue.get(), self.entradas.get())).pack(side=tk.BOTTOM)


class PopUpEgreso(PopUp):
    entradas = None

    def __init__(self, root):
        super().__init__(root)
        self.eVueltas = tk.Entry(master=self.root, justify="center", width="16")

    def cargueCampos(self):
        lVueltas = tk.Label(master=self.root, text="Vueltas")
        lVueltas.pack(pady="4")
        self.eVueltas.configure(font=("Courier", 11))
        self.eVueltas.pack()
        self.entradas = ttk.Combobox(master=self.root, state="readonly")
        opcionesEntrada = Finanzas.getCategoriesAndSubcat().to_dict()
        aux = []
        for i in range(len(opcionesEntrada["ITEM"])):
            aux.append(str(opcionesEntrada["ITEM"][i]))
        self.entradas['values'] = aux
        # self.entradas.set("REPARTIR")
        self.entradas.pack(padx="20", pady="6")

    def cargueBoton(self):
        tk.Button(master=self.root, text="Subir",
                  command=Finanzas.insertSalida(self.getTotal(), self.entradas.get())).pack()

    def getTotal(self):
        try:
            return int(self.eValue.get()) - int(self.eVueltas.get())
        except:
            return ''


a = App()
a.start()
a.end()
