from dominio.connection import ConnectionSql
from datetime import datetime
from dateutil import relativedelta
from types import SimpleNamespace
import json


class Fecha:
    def __init__(self, frmt):
        self.format = str(frmt)
        self.today = datetime.now()
        self.initDate = datetime(self.today.year, self.today.month, 1)
        aux = self.today + relativedelta.relativedelta(months=1)
        self.nextDate = datetime(aux.year, aux.month, 1)

    def getCurrentDate(self):
        return self.today

    def getInitialDate(self):
        return self.initDate

    def getNextDate(self):
        return self.nextDate

    def getCurrentDateF(self):
        return self.today.strftime(self.format)

    def getInitialDateF(self):
        return self.initDate.strftime(self.format)

    def getNextDateF(self):
        return self.nextDate.strftime(self.format)


class Finanzas:
    con = ConnectionSql()
    fecha = Fecha('%x')
    hoy = fecha.getCurrentDate()
    nextFecha = fecha.getNextDate()
    initFecha = fecha.getInitialDate()
    saldos = None

    query = "SELECT * FROM CATEGORIAS WHERE VF = 'F' AND M =" + str(hoy.strftime('%m')) + " AND A =" + \
            str(hoy.strftime('%y')) + " order by cat asc"

    @staticmethod
    def cursor():
        return Finanzas.con.getCursor()

    @staticmethod
    def cargarSaldos():
        Finanzas.con.execFunction("getSaldos", [Finanzas.fecha.getInitialDateF()])
        for i in Finanzas.cursor():
            Finanzas.saldos = json.loads(i[0], object_hook=lambda d: SimpleNamespace(**d))

    @staticmethod
    def getGastos():
        Finanzas.con.execute("SELECT Compra, Costo, descripcion FROM COMPRAS WHERE (M = {0} AND A ={1}) OR (M =-1 AND "
                             "PAGADO = 0)".format(Finanzas.initFecha.strftime('%m'), Finanzas.initFecha.strftime('%Y')))
        return Finanzas.getDataTabla(Finanzas.cursor())

    @staticmethod
    def getDataTabla(cursor):
        return {"titles": Finanzas.getTitles(cursor),
                "data": Finanzas.getData(cursor),
                "widths": Finanzas.getWidths(cursor)}

    @staticmethod
    def getData(cursor):
        items = []
        for item in cursor:
            if len(item) == 1:
                items.append(item[0])
            else:
                items.append(Finanzas.convertToArr(item))
        return items

    @staticmethod
    def getJData(cursor):
        return json.loads(cursor.fetchone()[0])

    @staticmethod
    def getTitles(cursor):
        titles = []
        for title in cursor.description:
            titles.append(title[0])
        return titles

    @staticmethod
    def getWidths(cursor):
        return [100, 100, 100, 100, 100]

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
        Finanzas.con.execute("select concat(concat(cat,' - '),vf) AS ITEM, mensual, saldoactual from categorias")
        return Finanzas.getDataTabla(Finanzas.cursor())

    @staticmethod
    def getCategoriesAndSubcat():
        Finanzas.con.execute("select concat(concat(categoria, ' - '), subcategoria) AS ITEM from subcategorias")
        return Finanzas.getData(Finanzas.cursor())

    @staticmethod
    def getCategorias():
        Finanzas.con.execute("select CAT from categorias")
        return Finanzas.getData(Finanzas.cursor())

    @staticmethod
    def getDeudas():
        Finanzas.con.execute("SELECT concat(concat(ACREEDOR, ' - '), MONTO) AS deuda FROM DEUDAS")
        aux = Finanzas.getDataTabla(Finanzas.cursor())
        if len(aux['data']) == 0:
            aux['data'].append(['Sin Deudas!'])
        return aux

    @staticmethod
    def getCategoriasByTipo(tipo):
        Finanzas.con.execute("SELECT * FROM CATEGORIAS WHERE VF = '{0}' FOR JSON AUTO".format(tipo))
        return Finanzas.getJData(Finanzas.cursor())

    @staticmethod
    def convertToArr(items):
        rta = []
        for item in items:
            rta.append(item)
        return rta

    @staticmethod
    def resetGastosMensuales():
        Finanzas.con.execute("UPDATE COMPRAS SET PAGADO = 0 WHERE M = '-1'")

    @staticmethod
    def insertEntrada(entrada, cat):
        if entrada != '' and cat != '':
            Finanzas.con.execProcedure('insertEntrada', [entrada, cat])


    @staticmethod
    def insertSalida(salida, cat):
        if salida != '' and cat != '':
            Finanzas.con.execProcedure('insertSalida', [salida, cat])

    @staticmethod
    def pagarDeuda(deudas):
        if deudas != "Sin deudas!":
            aux = str(deudas).split("-")
            Finanzas.con.execProcedure("deudaPagada", aux)
        else:
            print("No tienes deudas crack")

    @staticmethod
    def itemComprado(item):
        Finanzas.con.execProcedure("itemComprado", [item])

    @staticmethod
    def aplazarCompra(item):
        Finanzas.con.execProcedure("aplazarCompra", [item])

    @staticmethod
    def execQueryNoSelect(query):
        Finanzas.con.execute(query)

    @staticmethod
    def pagarCategoriasVar(restante):
        saldosVar = Finanzas.getCategoriasByTipo('V')
        pagado = 0
        for i in range(len(saldosVar)):
            M = Finanzas.nextFecha.month
            A = Finanzas.nextFecha.year
            money = int(saldosVar[i]["SALDOACTUAL"]) + (int(saldosVar[i]["MENSUAL"]) * restante / 100)
            pagado += int(saldosVar[i]["MENSUAL"]) * int(restante) / 100
            Finanzas.con.execute("UPDATE CATEGORIAS SET SALDOACTUAL={0}, M={1}, A={2} WHERE CAT = '{3}'"
                                 .format(money, M, A, saldosVar[i]["CAT"]))
        return pagado

    @staticmethod
    def pagarCategoriasFijas(cuotas):
        saldosFijos = Finanzas.getCategoriasByTipo('F')
        pagado = 0
        #  Pagar lo fijo
        for i in range(len(saldosFijos)):
            nextFecha = Finanzas.hoy + relativedelta.relativedelta(months=4 * cuotas[i])
            M = nextFecha.month
            A = nextFecha.year
            money = int(saldosFijos[i]["SALDOACTUAL"]) + (int(saldosFijos[i]["MENSUAL"]) * cuotas[i])
            pagado += int(saldosFijos[i]["MENSUAL"]) * int(cuotas[i])
            Finanzas.con.execute("UPDATE CATEGORIAS SET SALDOACTUAL={0}, M={1}, A={2} WHERE CAT = '{3}'"
                                 .format(money, M, A, saldosFijos[i]["CAT"]))
        return pagado

    @staticmethod
    def repartirDinero():
        categoriasFijas = Finanzas.getCategoriasByTipo('F')
        Finanzas.getSummaryCategorias()
        opcion = input("Ok? y/n/CANCELAR ") or "y"
        if opcion.upper() == "CANCELAR":
            Finanzas.con.NoOkay()
            return
        elif opcion.upper() == "Y":
            # Actualizar categorias, sumar en saldo actual, y sumarle uno al mes (si no da 12, sino = 1) y año
            pagoFijos = Finanzas.pagarCategoriasFijas([1 for i in range(len(categoriasFijas))])
            pagoVar = Finanzas.pagarCategoriasVar(Finanzas.saldos.Repartible - pagoFijos)

        else:
            aux = Finanzas.createCuotasCategorias(categoriasFijas)
            cuotas = aux['cuotas']
            dinVar = aux['dineroVar']
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
                print(Finanzas.saldos.Repartible - pagoFijos)
                pagoVar = Finanzas.pagarCategoriasVar(int(restante))
        print()
        print("PAGOS FIJOS: ", pagoFijos)
        print("PAGOS VAR: ", pagoVar)
        Finanzas.con.execute("UPDATE CATEGORIAS SET SALDOACTUAL = {0} WHERE CAT = 'REPARTIR'"
                             .format(Finanzas.saldos.Repartible - pagoFijos - pagoVar))
        confirm = input("GUARDAR CAMBIOS? y/n ") or "y"
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

    @staticmethod
    def insertar(tabla, **kwargs):
        # Finanzas.insertar('ENTRADAS', **{"monto": entrada, "categoria": cat})
        keys = '('
        values = '('
        for key, value in kwargs.items():
            keys += "{0},".format(key)
            values += "'{0}',".format(value)
        keys = keys[:len(keys) - 1]
        values = values[:len(values) - 1]
        query = "INSERT INTO {0} {1} VALUES {2} ".format(tabla, keys + ')', values + ')')
        print(query)
        Finanzas.con.execute(query)
        print("insert realizado")

    @staticmethod
    def getSummaryCategorias():
        categoriasFijas = Finanzas.getCategoriasByTipo('F')
        print("dinero actual: \033[1m{0}\033[0m".format(Finanzas.saldos.Repartible))
        print()
        dinVar = 0
        for i in range(0, len(categoriasFijas), 2):
            try:
                print('{:<18}{:<15} {:<18}{:<10}'.format(categoriasFijas[i]["CAT"],
                                                         '\033[1m' + str(categoriasFijas[i]["MENSUAL"]) + '\033[0m',
                                                         categoriasFijas[i + 1]["CAT"],
                                                         '\033[1m' + str(
                                                             categoriasFijas[i + 1]["MENSUAL"]) + '\033[0m'))
                dinVar += categoriasFijas[i]["MENSUAL"] + categoriasFijas[i + 1]["MENSUAL"]
            except Exception:
                print('{:<18} \033[1m{:<15}\033[0m'.format(categoriasFijas[i]["CAT"], categoriasFijas[i]["MENSUAL"]))
                dinVar += categoriasFijas[i]["MENSUAL"]
        dinVar = Finanzas.saldos.Repartible - dinVar
        print("Dinero variable a repartir: \033[1m{0}\033[0m".format(dinVar))

    @staticmethod
    def createCuotasCategorias(categoriasFijas):
        cuotas = []
        dinVar = Finanzas.saldos.Repartible
        print("Para excluir un pago escriba N")
        print("Se recomienda dejar para los variables 200.000")
        print("{:<18}{:<15}{:<5}".format("Repartir", "Categoria", "Cuotas"))
        for j in range(len(categoriasFijas)):
            try:
                x = input("{:<18} {:<15}"
                          .format(dinVar, categoriasFijas[j]["CAT"]))
                if x.upper() == "N":
                    cuotas.append(0)
                else:
                    cuotas.append(int(x))
            except ValueError:
                cuotas.append(1)
            finally:
                dinVar -= categoriasFijas[j]["MENSUAL"] * cuotas[j]
        dinVar = Finanzas.saldos.Repartible
        print("{:<12}{:<18}{:<5}".format("Categoria", "Pago", "Cuotas"))
        for i in range(len(categoriasFijas)):
            dinVar -= categoriasFijas[i]["MENSUAL"] * cuotas[i]
            if cuotas[i] != 0:
                print("{:<12}{:<18}{:<5}"
                      .format(categoriasFijas[i]["CAT"], categoriasFijas[i]["MENSUAL"] * cuotas[i], cuotas[i]))
        print("Dinero a repartir: ", dinVar)
        return {"cuotas": cuotas, "dineroVar": dinVar}
