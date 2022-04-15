from tkinter import ttk, Toplevel
import tkinter as tk
from controller.Finanzas import Finanzas


class PopUp:
    """
    Ventana que puede ser una entrada o salida
    """

    def __init__(self, root, lines=1):
        self.lines = lines
        self.root = Toplevel(root)
        self.root.geometry("{0}x{1}+{2}+{3}".format(
            round(self.root.winfo_screenwidth() / 2), round(self.root.winfo_screenheight() / 2),
            round(self.root.winfo_screenwidth() / 4), round(self.root.winfo_screenheight() / 4)))

        self.cargueCampos()
        self.cargueBoton()

    def cargueCampos(self):
        pass

    def cargueBoton(self):
        pass


class PopUpIngreso(PopUp):
    entradas = None

    def __init__(self, root):
        self.eValue = None
        super().__init__(root)

    def cargueCampos(self):
        self.eValue = EntryRequired({"db": "Valor", "title": "Valor"}, self.root, tk.TOP)
        self.entradas = ttk.Combobox(master=self.root, state="readonly")
        self.entradas['values'] = Finanzas.getCategorias()
        self.entradas.set("REPARTIR")
        self.entradas.pack(padx="20", pady="6")

    def cargueBoton(self):
        tk.Button(master=self.root, text="Subir",
                  command=self.insertEntrada).pack()
        pass

    def insertEntrada(self):
        Finanzas.insertEntrada(self.eValue.get(), self.entradas.get())


class PopUpEgreso(PopUp):
    entradas = None

    def __init__(self, root):
        self.eValue = None
        self.eVueltas = None
        super().__init__(root)

    def cargueCampos(self):
        self.eValue = EntryRequired({"db": "Valor", "title": "Valor"}, self.root, tk.TOP)
        self.eVueltas = EntryNotRequired('Vueltas', self.root, tk.TOP)
        self.entradas = ttk.Combobox(master=self.root, state="readonly")
        self.entradas['values'] = Finanzas.getCategoriesAndSubcat()
        self.entradas.pack(padx="20", pady="6")

    def cargueBoton(self):
        tk.Button(master=self.root, text="Subir",
                  command=Finanzas.insertSalida(self.getTotal(), self.entradas.get())).pack(pady=15)

    def getTotal(self):
        pass
        try:
            return int(self.eValue.get()) - int(self.eVueltas.get())
        except:
            return ''


class PopUpGasto(PopUp):
    def __init__(self, root, lines=2):
        self.buttonsRequired = []
        self.othersButtons = []
        super().__init__(root, lines)

    def validate(self, *args):
        for but in self.buttonsRequired:
            but.draw()

    def cargueBoton(self):
        tk.Button(master=self.root, text="Subir",
                  command=self.agregar).pack(pady=15)

    def agregar(self):
        flag = True
        self.root.bind("<KeyPress>", self.validate)
        for but in self.buttonsRequired:
            but.draw()
            if not but.isValid():
                flag = False
        if flag:
            #Realizar json
            rta = {}
            for but in self.buttonsRequired:
                rta[but.getNameDb()] = but.getValue()
            for but in self.othersButtons:
                rta[but.getNameDb()] = but.getValue()
            Finanzas.insertar("COMPRAS", **rta)
            self.root.destroy()


    def cargueCampos(self):
        campos = [{'names': {'title':'Compra', 'db': 'Compra'}, 'required': True},
                  {'names': {'title':'Subcategoria', 'db': 'Subcategoria'}, 'required': True},
                  {'names': {'title':'Categoria', 'db': 'CAT'},  'required': True},
                  {'names': {'title':'Costo', 'db': 'COSTO'}, 'required': True},
                  {'names': {'title':'M', 'db': 'M'}, 'required': True},
                  {'names': {'title':'A', 'db': 'A'}, 'required': True},
                  {'names': {'title':'Descripcion','db': 'Descripcion'}, 'required': False}]
        itemsPerLine = round(len(campos) / self.lines)
        aux = 0
        for line in range(0, self.lines):
            frame = tk.Frame(master=self.root)
            frame.pack()
            limit = aux + itemsPerLine
            if limit > len(campos):
                limit = len(campos)
            self.appendCampos(frame, campos[aux:limit])
            aux += itemsPerLine

    def appendCampos(self, fr, campos):
        for campo in campos:
            if bool(campo['required']):
                self.buttonsRequired.append(EntryRequired(campo['names'], fr, tk.LEFT))
            else:
                self.othersButtons.append(EntryNotRequired(campo['names'], fr, tk.LEFT))


class EntryForm:
    def __init__(self, name, root, side):
        self.root = tk.Frame(master=root)
        self.text = tk.Label(master=self.root, text=name['title'], anchor="w")
        self.entry = tk.Entry(master=self.root)
        self.nameDb = name['db']
        self.pack(side)

    def isValid(self):
        pass

    def draw(self):
        pass

    def pack(self, side):
        self.root.pack(side=side, padx=20)
        self.entry.pack(side=tk.BOTTOM)
        self.text.pack(side=tk.TOP)

    def getNameDb(self):
        return self.nameDb

    def getValue(self):
        return self.entry.get()

    def getName(self):
        return self.text.cget("text")


class EntryNotRequired(EntryForm):
    def __init__(self, name, root, side):
        super().__init__(name, root, side)

    def isValid(self):
        return True

    def draw(self):
        self.entry.config(bd=0, highlightthickness=0, highlightbackground="white")


class EntryRequired(EntryForm):
    def __init__(self, name, root, side):
        super().__init__(name, root, side)

    def isValid(self):
        valid = True
        if self.entry.get() == '':
            valid = False
        return valid

    def draw(self, *args):
        if not (self.isValid()):
            self.entry.config(bd=1, highlightthickness=1, highlightbackground="red")
        else:
            self.entry.config(bd=0, highlightthickness=0, highlightbackground="white")

    def get(self):
        return self.entry.get()
