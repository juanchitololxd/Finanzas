from connection import *
from datetime import datetime
from datetime import timedelta
import tkinter as tk
root = tk.Tk()
hoy = datetime.now()
nextFecha = hoy + timedelta(weeks=6)  # proximo mes
con = Connection()
Query = "SELECT * FROM CATEGORIAS WHERE VF = 'F' AND M =" + str(hoy.month) + " AND A =" + str(hoy.year) +\
        " order by cat asc"
saldosFijos = pd.read_sql(Query, con=con.con).to_dict()
Query3 = "SELECT * FROM CATEGORIAS WHERE VF = 'V'"
saldosVar = pd.read_sql(Query3, con.con).to_dict()

def terminar():
    con.close()
    root.destroy()

def insertEntrada(entrada,cat):
    query = "INSERT INTO ENTRADAS (monto, categoria) VALUES (" + str(entrada) + ",'" +str(cat) + "')"
    con.execOther(query)


def insertSalida(salida, opcion):
    query = "INSERT INTO SALIDAS (monto, categoria) VALUES ('" + str(salida) + "','" + str(opcion) + "')"
    con.execOther(query)


def repartirDinero():
    total = pd.read_sql("SELECT SALDOACTUAL FROM CATEGORIAS WHERE CAT ='REPARTIR'", con=con.con).to_dict()
    saldosFijos = pd.read_sql(Query, con=con.con).to_dict()
    print("dinero actual: ", '\033[1m',total["SALDOACTUAL"][0], '\033[0m')
    print()
    #Traer cuanto hay que pagar de valores fijos
    #Fecha actual sea mayor a la de oracle

    dinVar = 0
    for i in range(0, len(saldosFijos["CAT"]), 2):
        try:
            print('{:<18}{:<15} {:<18}{:<10}'.format(saldosFijos["CAT"][i],
                                                    '\033[1m'+str(saldosFijos["MENSUAL"][i])+'\033[0m',
                                                    saldosFijos["CAT"][i+1],
                                                    '\033[1m'+str(saldosFijos["MENSUAL"][i+1])+'\033[0m'))
            dinVar += saldosFijos["MENSUAL"][i] + saldosFijos["MENSUAL"][i + 1]
        except KeyError:
            print('{:<18}{:<15} '.format(saldosFijos["CAT"][i], '\033[1m'+str(saldosFijos["MENSUAL"][i])+'\033[0m'))
            dinVar += saldosFijos["MENSUAL"][i]


    dinVar = total["SALDOACTUAL"][0] - dinVar

    print("Dinero variable a repartir: ", '\033[1m', dinVar, '\033[0m'," Ok? y/n/CANCELAR ")
    opcion = input() or "y"
    cuotas = []
    if opcion.upper() == "CANCELAR":
        con.NoOkay()
        return
    elif opcion.upper() == "Y":
        # Actualizar categorias, sumar en saldo actual, y sumarle uno al mes (si no da 12, sino = 1) y año
        cuotas = [1 for i in range(len(saldosFijos["CAT"]))]
        pagoFijos = pagarCategoriasFijas(cuotas)
        pagoVar = pagarCategoriasVar(total["SALDOACTUAL"][0]-pagoFijos)

    else:
        dinVar = total["SALDOACTUAL"][0]
        print("Para excluir un pago fijo, escriba n")
        for j in range(len(saldosFijos["CAT"])):
            try:
                x = input("Recomendado: 200.000 Saldo a repartir: \033[1m{}\033[0m. N° Cuotas {} ".format(dinVar, saldosFijos["CAT"][j]))
                if x.upper() == "N":
                    cuotas.append(0)
                else:
                    cuotas.append(int(x))
            except ValueError:
                cuotas.append(1)
            finally:
                dinVar -= saldosFijos["MENSUAL"][j] * cuotas[j]
        dinVar = total["SALDOACTUAL"][0]
        for i in range(len(saldosFijos["CAT"])):
            dinVar -= saldosFijos["MENSUAL"][i]*cuotas[i]
            if cuotas[i] != 0:
                print(saldosFijos["CAT"][i], saldosFijos["MENSUAL"][i], cuotas[i])
        print("Dinero a repartir: ", dinVar)
        confirm = input("Dinero fijo se repartirá, reparto lo variable? y/n/cancelar ") or "y"
        if confirm.upper() == "CANCELAR":
            con.NoOkay()
            return

        elif confirm.upper() == "Y":
            pagoFijos = pagarCategoriasFijas(cuotas)
            pagoVar =pagarCategoriasVar(dinVar)
        else:
            pagoFijos = pagarCategoriasFijas(cuotas)
            restante = input("Digite el valor a repartir en las categorias variables ")
            print(pagoFijos)
            print(total["SALDOACTUAL"][0] - pagoFijos)
            pagoVar = pagarCategoriasVar(int(restante))
    print()
    print("PAGOS FIJOS: ", pagoFijos)
    print("PAGOS VAR: ", pagoVar)
    con.execInsNoCommit("UPDATE CATEGORIAS SET SALDOACTUAL = " + str(total["SALDOACTUAL"][0]-pagoFijos-pagoVar) +
                  " WHERE CAT = 'REPARTIR'")
    confirm = input("REVERTIR CAMBIOS? y/n ") or "y"

    if confirm.upper() != "Y":
        con.okay()
    else:
        con.NoOkay()


def execSql(tipo, query):
    if tipo == "SELECT":
        print(con.execSelectPd(str(query)))
    else:
        con.execOther(str(query))


def pagarCategoriasFijas(cuotas):
    saldosFijos = pd.read_sql(Query, con=con.con).to_dict()
    pagado = 0
    #  Pagar lo fijo
    for i in range(len(saldosFijos["CAT"])):
        nextFecha = hoy + timedelta(weeks=4*cuotas[i])
        M = nextFecha.month
        A = nextFecha.year
        money = int(saldosFijos["SALDOACTUAL"][i]) + (int(saldosFijos["MENSUAL"][i]) * cuotas[i])
        pagado += int(saldosFijos["MENSUAL"][i]) * int(cuotas[i])
        aux ="UPDATE CATEGORIAS SET SALDOACTUAL=" \
             + str(money) + ", M ="+str(M)+ ", A=" + str(A) + " WHERE CAT='" + str(saldosFijos["CAT"][i]) + "'"
        con.execInsNoCommit(aux)

    return pagado

def pagarCategoriasVar(restante):
    saldosVar = pd.read_sql(Query3, con.con).to_dict()
    pagado = 0
    for i in range(len(saldosVar["CAT"])):
        M = nextFecha.month
        A = nextFecha.year
        money = int(saldosVar["SALDOACTUAL"][i]) + (int(saldosVar["MENSUAL"][i]) * restante/100)
        pagado += int(saldosVar["MENSUAL"][i]) * int(restante)/100
        aux ="UPDATE CATEGORIAS SET SALDOACTUAL=" \
             + str(money) + ", M ="+str(M)+ ", A=" + str(A) \
             + " WHERE CAT='" + str(saldosVar["CAT"][i]) + "'"
        con.execInsNoCommit(aux)

    return pagado

def pagarDeuda(Deudas):
    if Deudas!= "Sin deudas!":
        aux = str(Deudas).split("-")
        query = "delete from deudas where monto = '" + str(aux[1]) + "' and acreedor ='" + str(aux[0]) + "'"
        con.execOther(query)
    else:
        print("No tienes deudas crack")