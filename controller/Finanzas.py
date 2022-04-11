from dominio.connection import ConnectionOracle
from datetime import datetime
from dateutil import relativedelta
import json


class Finanzas:
    con = ConnectionOracle("jp", "jp2")
    hoy = datetime.now()
    saldos = {}
    nextFecha = hoy + relativedelta.relativedelta(months=1)  # proximo mes
    query = "SELECT * FROM CATEGORIAS WHERE VF = 'F' AND M =" + str(hoy.month) + " AND A =" + str(hoy.year) + \
            " order by cat asc"

    @staticmethod
    def cargarSaldos():
        Finanzas.saldos = Finanzas.getFunctionJson("getSaldos(TO_DATE('" + str(Finanzas.hoy).split()[0] +
                                                   "','YYYY-mm-dd'))")[0]

    @staticmethod
    def execProcedure(proc, params=None):
        """
        Ejecuta un procedure
        :param proc: Nombre del procedure
        :param params: Lista de parametros del procedure. Default []
        :return:
        """
        if params is None:
            params = []
        Finanzas.con.execProcedure(proc, params)
        pass

    @staticmethod
    def getFunctionJson(func):
        """
        Procesa una función que devuelve un Json
        :param func: nombre función
        :return: Lista con los items de tipo json
        """
        Finanzas.con.execFunction(Finanzas.con.getQueryFunction(func))
        aux = []
        for ix, resultSet in enumerate(Finanzas.con.getCursor().getimplicitresults()):
            for row in resultSet:
                aux.append(json.loads(row[0]))
        return aux

    @staticmethod
    def getSelect(query):
        return Finanzas.con.execSelect(query)

    @staticmethod
    def getGastos():
        return Finanzas.con.execSelectPd("SELECT Compra, Costo, descripcion FROM COMPRAS " +
                                         "WHERE (A =" + str(Finanzas.hoy.year) + " AND M =" +
                                         str(Finanzas.hoy.month) + ") OR (M =-1 AND PAGADO = 0)")

    @staticmethod
    def getMonth(numMonth):
        return {
            1: 'Enero',
            2: 'Feb',
            3: 'Marzo',
            4: 'Abril',
            5: 'Mayo',
            6: 'Junio',
            7: 'Julio',
            8: 'Agosto',
            9: 'Sept',
            10: 'Oct',
            11: 'Nov',
            12: 'Dic'
        }[numMonth]

    @staticmethod
    def getCategoriesAndVF():
        return Finanzas.con.execSelectPd("select concat(concat(cat,' - '),vf) AS ITEM, mensual, saldoactual "
                                         "from categorias")

    @staticmethod
    def getCategoriesAndSubcat():
        aux = []
        for item in Finanzas.con.execSelect("select concat(concat(categoria, ' - '), subcategoria) AS ITEM from "
                                            "subcategorias "):
            aux.append(item[0])
        return aux

    @staticmethod
    def getCategories():
        aux = []
        for item in Finanzas.con.execSelect("select CAT from categorias "):
            aux.append(item[0])
        return aux

    @staticmethod
    def insertEntrada(entrada, cat):
        if entrada != '' and cat != '':
            query = "INSERT INTO ENTRADAS (monto, categoria) VALUES (" + str(entrada) + ",'" + str(cat) + "')"
            Finanzas.con.execInsNoCommit(query)

    @staticmethod
    def insertSalida(salida, opcion):
        if salida != '' and opcion != '':
            query = "INSERT INTO SALIDAS (monto, categoria) VALUES ('" + str(salida) + "','" + str(opcion) + "')"
            Finanzas.con.execInsNoCommit(query)

    @staticmethod
    def pagarDeuda(deudas):
        if deudas != "Sin deudas!":
            aux = str(deudas).split("-")
            query = "delete from deudas where monto = '" + str(aux[1]) + "' and acreedor ='" + str(aux[0]) + "'"
            Finanzas.con.execInsNoCommit(query)
        else:
            print("No tienes deudas crack")

    @staticmethod
    def pagarCategoriasVar(restante):
        saldosVar = Finanzas.con.execSelectPd("SELECT * FROM CATEGORIAS WHERE VF = 'V'").to_dict()
        pagado = 0
        for i in range(len(saldosVar["CAT"])):
            M = Finanzas.nextFecha.month
            A = Finanzas.nextFecha.year
            money = int(saldosVar["SALDOACTUAL"][i]) + (int(saldosVar["MENSUAL"][i]) * restante / 100)
            pagado += int(saldosVar["MENSUAL"][i]) * int(restante) / 100
            aux = "UPDATE CATEGORIAS SET SALDOACTUAL=" \
                  + str(money) + ", M =" + str(M) + ", A=" + str(A) \
                  + " WHERE CAT='" + str(saldosVar["CAT"][i]) + "'"
            Finanzas.con.execInsNoCommit(aux)
        return pagado

    @staticmethod
    def pagarCategoriasFijas(cuotas):
        saldosFijos = Finanzas.con.execSelectPd(Finanzas.query).to_dict()
        pagado = 0
        #  Pagar lo fijo
        for i in range(len(saldosFijos["CAT"])):
            nextFecha = Finanzas.hoy + relativedelta.relativedelta(months=4 * cuotas[i])
            M = nextFecha.month
            A = nextFecha.year
            money = int(saldosFijos["SALDOACTUAL"][i]) + (int(saldosFijos["MENSUAL"][i]) * cuotas[i])
            pagado += int(saldosFijos["MENSUAL"][i]) * int(cuotas[i])
            aux = "UPDATE CATEGORIAS SET SALDOACTUAL=" \
                  + str(money) + ", M =" + str(M) + ", A=" + str(A) + " WHERE CAT='" + str(saldosFijos["CAT"][i]) + "'"
            Finanzas.con.execInsNoCommit(aux)

        return pagado

    @staticmethod
    def execOtherSql(query):
        Finanzas.con.execInsNoCommit(query)

    @staticmethod
    def getCategorias():
        return Finanzas.con.execSelectPd(Finanzas.query).to_dict()

    @staticmethod
    def repartirDinero():
        total = Finanzas.con.execSelectPd("SELECT SALDOACTUAL FROM CATEGORIAS WHERE CAT ='REPARTIR'").to_dict()
        saldosFijos = Finanzas.getCategorias()
        print("dinero actual: ", '\033[1m', total["SALDOACTUAL"][0], '\033[0m')
        print()
        # Traer cuanto hay que pagar de valores fijos
        # Fecha actual sea mayor a la de oracle

        dinVar = 0
        for i in range(0, len(saldosFijos["CAT"]), 2):
            try:
                print('{:<18}{:<15} {:<18}{:<10}'.format(saldosFijos["CAT"][i],
                                                         '\033[1m' + str(saldosFijos["MENSUAL"][i]) + '\033[0m',
                                                         saldosFijos["CAT"][i + 1],
                                                         '\033[1m' + str(saldosFijos["MENSUAL"][i + 1]) + '\033[0m'))
                dinVar += saldosFijos["MENSUAL"][i] + saldosFijos["MENSUAL"][i + 1]
            except KeyError:
                print('{:<18}{:<15} '.format(saldosFijos["CAT"][i],
                                             '\033[1m' + str(saldosFijos["MENSUAL"][i]) + '\033[0m'))
                dinVar += saldosFijos["MENSUAL"][i]

        dinVar = total["SALDOACTUAL"][0] - dinVar

        print("Dinero variable a repartir: ", '\033[1m', dinVar, '\033[0m', " Ok? y/n/CANCELAR ")
        opcion = input() or "y"
        cuotas = []
        if opcion.upper() == "CANCELAR":
            Finanzas.con.NoOkay()
            return
        elif opcion.upper() == "Y":
            # Actualizar categorias, sumar en saldo actual, y sumarle uno al mes (si no da 12, sino = 1) y año
            cuotas = [1 for i in range(len(saldosFijos["CAT"]))]
            pagoFijos = Finanzas.pagarCategoriasFijas(cuotas)
            pagoVar = Finanzas.pagarCategoriasVar(total["SALDOACTUAL"][0] - pagoFijos)

        else:
            dinVar = total["SALDOACTUAL"][0]
            print("Para excluir un pago fijo, escriba n")
            for j in range(len(saldosFijos["CAT"])):
                try:
                    x = input("Recomendado: 200.000 Saldo a repartir: \033[1m{}\033[0m. N° Cuotas {} "
                              .format(dinVar, saldosFijos["CAT"][j]))
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
                dinVar -= saldosFijos["MENSUAL"][i] * cuotas[i]
                if cuotas[i] != 0:
                    print(saldosFijos["CAT"][i], saldosFijos["MENSUAL"][i], cuotas[i])
            print("Dinero a repartir: ", dinVar)
            confirm = input("Dinero fijo se repartirá, reparto lo variable? y/n/cancelar ") or "y"
            if confirm.upper() == "CANCELAR":
                Finanzas.con.NoOkay()
                return

            elif confirm.upper() == "Y":
                pagoFijos = Finanzas.pagarCategoriasFijas(cuotas)
                pagoVar = Finanzas.pagarCategoriasVar(dinVar)
            else:
                pagoFijos = Finanzas.pagarCategoriasFijas(cuotas)
                restante = input("Digite el valor a repartir en las categorias variables ")
                print(pagoFijos)
                print(total["SALDOACTUAL"][0] - pagoFijos)
                pagoVar = Finanzas.pagarCategoriasVar(int(restante))
        print()
        print("PAGOS FIJOS: ", pagoFijos)
        print("PAGOS VAR: ", pagoVar)
        Finanzas.con.execInsNoCommit("UPDATE CATEGORIAS SET SALDOACTUAL = " + str(total["SALDOACTUAL"][0] - pagoFijos -
                                                                                  pagoVar) + " WHERE CAT = 'REPARTIR'")
        confirm = input("REVERTIR CAMBIOS? y/n ") or "y"
        Finanzas.saveChanges(confirm)

    @staticmethod
    def close():
        Finanzas.con.close()

    @staticmethod
    def saveChanges(confirm):
        if confirm.upper() == "Y":
            Finanzas.con.okay()
        else:
            Finanzas.con.NoOkay()
