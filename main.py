import tkinter
from tkinter import ttk

from funciones import *
# Configuracion basica de la app

pad = 3
_geom = '200x200+0+0'
root.geometry("{0}x{1}+0+0".format(
    root.winfo_screenwidth() - pad, root.winfo_screenheight() - pad))
root.title("FinanzasJP")



# Funciones
def insEntrada():
    insertEntrada(str(eEntry.get()), str(Entradas.get()))

def pagDeuda():
    pagarDeuda(Deudas.get())


def insSalida():
    if str(eExitVueltas.get()) == "":
        insertSalida(str(int(eExit.get())), str(options.get().split(" - ")[0]))
    else:
        insertSalida(str(int(eExit.get()) - int(eExitVueltas.get())), str(options.get().split(" - ")[0]))


def exectSql():
    aQuery = str(sql.get()).split()
    execSql("SELECT" if aQuery[0].upper() == "SELECT" else "0", sql.get())

def comprar():
    print()

def aplazar():
    print()

# Deudas
allDeudas = pd.read_sql(" SELECT * FROM DEUDAS ORDER BY ACREEDOR", con=con.con).to_dict()

fDeudas = tk.Frame()
fDeudas.config(bg="#B8A5A1")
fDeudas.pack(side=tk.LEFT, fill="y")

lDeudas = tk.Label(master=fDeudas, text=" Mis Deudas ")
lDeudas.pack(pady="6", fill="x")
lDeudas.config(bg="#B8A5A1")

aux = []
Deudas = ttk.Combobox(master=fDeudas, state="readonly")
length = len(allDeudas["MONTO"])
aux2 = ""
if length > 0:
    for i in range(len(allDeudas["MONTO"])):
        if i == 0:
            aux2 = str(allDeudas["ACREEDOR"][i]) + "-" + str(allDeudas["MONTO"][i])
        aux.append(str(allDeudas["ACREEDOR"][i]) + "-" + str(allDeudas["MONTO"][i]))
    Deudas['values'] = aux
    Deudas.set(aux2)
else:
    Deudas['values'] = aux
    Deudas.set("Sin deudas!")
# width="numero"
Deudas.pack(padx="20", pady="6")

bDeudas = tk.Button(master=fDeudas, text="pagar deuda", command=pagDeuda)
bDeudas.pack(pady="10")

#compras
allCompras = pd.read_sql(" SELECT * FROM COMPRAS ORDER BY m asc", con=con.con).to_dict()

fCompras = tk.Frame()
fCompras.config(bg="#B8A5A1")
fCompras.pack(side=tk.LEFT, fill="y")

lCompras = tk.Label(master=fDeudas, text=" Mis Compras ")
lCompras.pack(pady="6", fill="x")
lCompras.config(bg="#B8A5A1")

listCompras = []
Compras = ttk.Combobox(master=fDeudas, state="readonly")
length = len(allCompras["COMPRA"])
aux3 = ""
if length > 0:
    for i in range(len(allCompras["COMPRA"])):
        if i == 0:
            aux3 = str(allCompras["COMPRA"][i]) + "-" + str(allCompras["COSTO"][i])
        listCompras.append(str(allCompras["COMPRA"][i]) + "-" + str(allCompras["COSTO"][i]))
    Compras['values'] = listCompras
    Compras.set(aux3)
else:
    Deudas['values'] = aux
    Deudas.set("Sin compras!")
# width="numero"
Compras.pack(padx="20", pady="6")


bComprado = tk.Button(master=fDeudas, text="Comprado", command=comprar)
bComprado.pack(pady="10")

bAplazar = tk.Button(master=fDeudas, text="Aplazar", command=aplazar)
bAplazar.pack(pady="10")


# Entradas

entry = tk.Frame()
entry.pack(pady="25")

lEntry = tk.Label(master=entry, text="Entrada")
lEntry.pack(pady="4")

eEntry = tk.Entry(master=entry, justify="center", width="16")
eEntry.configure(font=("Courier", 11))
eEntry.pack(pady="4")

aux = []
Entradas = ttk.Combobox(master=entry, state="readonly")
opcionesEntrada = pd.read_sql(" SELECT CAT FROM CATEGORIAS ORDER BY CAT ASC", con=con.con).to_dict()
for i in range(len(opcionesEntrada["CAT"])):
    aux.append(str(opcionesEntrada["CAT"][i]))
Entradas['values'] = aux
Entradas.set("REPARTIR")
Entradas.pack(padx="20", pady="6")

bEntry = tk.Button(master=entry, text="Subir", command=insEntrada)
bEntry.pack(pady="4")

# Salidas Dinero total

exit = tk.Frame()
exit.pack(pady="10")

lExit = tk.Label(master=exit, text="Salida")
lExit.pack()

eExit = tk.Entry(master=exit, justify="center", width="16")
eExit.configure(font=("Courier", 11))
eExit.pack(pady="5", ipady="3")

# Salidas vueltas

lExitVueltas = tk.Label(master=exit, text="Vueltas")
lExitVueltas.pack()

eExitVueltas = tk.Entry(master=exit, justify="center", width="13")
eExitVueltas.configure(font=("Courier", 11))
eExitVueltas.pack(pady="6", ipady="3")

# Categorias
opciones = pd.read_sql(" SELECT * FROM SUBCATEGORIAS ORDER BY CATEGORIA", con=con.con).to_dict()

aux = []
maxLength = 0
item = ""
item2 = ""
for i in range(0, len(opciones["CATEGORIA"])):
    item = str(opciones["CATEGORIA"][i]) + " - " + str(opciones["SUBCATEGORIA"][i])
    aux.append(item)
    if len(item) > maxLength:
        maxLength = len(item)
        item2 = item
options = ttk.Combobox(master=exit, state="readonly", width=maxLength)
options['values'] = aux
options.set(item2)

options.pack(pady="13")

bExitVueltas = tk.Button(master=exit, text="Subir Salida", command=insSalida)
bExitVueltas.pack()

# Ejecutar sql
fSql = tk.Frame()
fSql.pack(pady="20")
lSql = tk.Label(master=fSql, text="SQL")
lSql.pack(side=tk.TOP)




sql = tk.Entry(master=fSql, justify="center", width="60")
sql.insert(0, "SELECT * FROM CATEGORIAS")
sql.configure(font=("Courier", 16))
sql.pack(ipady="5", side=tk.LEFT, fill=tk.X, padx="20")
"""
tSql = ttk.Combobox(master=fSql, state="readonly", width="7")
tSql['values'] = ['SELECT', 'OTHER']
tSql.set('SELECT')
tSql.pack(side=tk.RIGHT, padx="10")
"""
bSql = tk.Button(master=root, text="Subir consulta", command=exectSql)
bSql.pack()

# Repartir dinero
repDinero = tk.Button(master=root, text="REPARTIR DINERO", command=repartirDinero)
repDinero.configure(font=("Courier", 14, "bold"))
repDinero.pack(ipady="5", pady="40")


repDinero2= tk.Button(master=root, text="REPARTIR DINERO", command=repartirDinero)
repDinero2.configure(font=("Courier", 14, "bold"))
repDinero2.pack()
repDinero3 = tk.Button(master=root, text="REPARTIR DINERO", command=repartirDinero)
repDinero3.configure(font=("Courier", 14, "bold"))
repDinero3.pack(ipady="5", pady="40")
repDinero4 = tk.Button(master=root, text="REPARTIR DINERO", command=repartirDinero)
repDinero4.configure(font=("Courier", 14, "bold"))
repDinero4.pack(ipady="5", pady="40")
repDinero5 = tk.Button(master=root, text="REPARTIR DINERO", command=repartirDinero)
repDinero5.configure(font=("Courier", 14, "bold"))
repDinero5.pack(ipady="5", pady="40")


root.mainloop()
try:
    terminar()
except:
    print()

print("APP CERRADA CORRECTAMENTE")
