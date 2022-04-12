from PopUp import PopUpEgreso, PopUpIngreso
from tkinter import Canvas
from Shared import *


class CuadroInfo:
    """
    Componente del panel principal que muestra información y
    ejecuta diferentes funciones al clickear sobre cada cuadro
    """
    w = 130
    h = 35
    padY = 2
    padX = 2

    def __init__(self, title, content, root, rigth, coordStart=(0, 0)):
        self.canvas = Canvas(root, height=self.h, width=self.w,
                             bd=1, highlightthickness=1, highlightbackground=color)  # borde
        self.canvas.create_text(coordStart[0], coordStart[1], text=title, fill='green')
        self.canvas.create_text(coordStart[0], coordStart[1] + 19, text=content, fill='green',
                                font=('Helvetica', '15', 'bold'))
        self.selectFunction(title)
        if rigth:
            self.canvas.pack(side=tk.RIGHT, padx=self.padX)
        else:
            self.canvas.pack(side=tk.LEFT, padx=self.padX)

    def check_hand(self, *args):  # runs on mouse motion
        self.canvas.config(cursor="hand2")

    def selectFunction(self, title):
        self.canvas.bind("<Motion>", self.check_hand)
        if title.upper() == "MES":
            self.canvas.bind("<Button-1>", Panel.setMes)
        elif title.upper() == "INGRESOS":
            self.canvas.bind("<Button-1>", Panel.openIngresos)
        elif title.upper() == "EGRESOS":
            self.canvas.bind("<Button-1>", Panel.openEgresos)
        elif title.upper() == "REPARTIBLE":
            self.canvas.bind("<Button-1>", Panel.repartir)
        elif title.upper() == "DEUDAS":
            self.canvas.bind("<Button-1>", Panel.openDeudas)


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
            'Mes': {'content': Finanzas.getMonth(Finanzas.hoy.month)},
            'Ingresos': {'content': Finanzas.saldos.Ingresos},
            'Egresos': {'content': Finanzas.saldos.Egresos},
            'Repartible': {'content': Finanzas.saldos.Repartible},
            'Total': {'content': Finanzas.saldos.Total},
            'Deudas': {'content': Finanzas.saldos.Deudas}
        }
        # self.canvas = Canvas()
        for item in self.items.keys():
            if i < 3:
                self.appendFila(self.filaInf, item, i)
                # self.createSeparador()
            else:
                self.appendFila(self.filaSup, item, i)
            i += 1

        self.filaSup.pack(side=tk.TOP, pady=5)
        self.filaInf.pack(side=tk.BOTTOM)

    def appendFila(self, fila, item, i):
        if i % 2 == 0:
            CuadroInfo(item, self.items[item]["content"], fila, True, (CuadroInfo.w / 2, 8))
        else:
            CuadroInfo(item, self.items[item]["content"], fila, True, (CuadroInfo.w / 2, 8))

    @staticmethod
    def repartir(*args):
        Finanzas.repartirDinero()

    @staticmethod
    def setMes(e):
        pass

    @staticmethod
    def openIngresos(*args):
        PopUpIngreso(app)

    @staticmethod
    def openEgresos(*args):
        PopUpEgreso(app)

    @staticmethod
    def openDeudas(*args):
        pass
