import cx_Oracle
import pandas as pd
import pyodbc


class Connection:
    def __init__(self, con):
        self.con = con
        print("conexion establecida")
        self.cursor = self.con.cursor()

    def execSelectPd(self, query):
        """
        Ejecuta un query de tipo select
        :param query: Consulta basica sql
        :return: DataFrame con el contenido indicado
        """
        return pd.read_sql(query, con=self.con)

    def execOtherPd(self, query):
        """
        Ejecuta un query de tipo insert o update
        :param query: Consulta basica sql
        """
        pd.read_sql(query, con=self.con)

    def execute(self, query):
        """
        Realiza un query, que va desde un select hasta un exec
        :param query: consulta
        """
        self.cursor.execute(query)

    def execProcedure(self, proc, params=None):
        pass

    def okay(self):
        """
        Commit de todos los cambios
        """
        self.con.commit()
        print("COMMIT REALIZADO!")

    def NoOkay(self):
        """
        RollBack de todos los cambios
        """
        self.cursor.rollback()
        #self.cursor.execute("ROLLBACK")
        print("ROLLBACK")

    def close(self):
        self.cursor.close()
        self.con.close()
        print("Conexion cerrada")

    def getCursor(self):
        return self.cursor

    @staticmethod
    def getQueryFunction(func, tipo="sys_refcursor"):
        """
        Empaqueta el nombre de la funcion en un string para que la funcion pueda ser leida correctamente
        :param func: nombre funcion con sus parametros (si tiene)
        :param tipo: Tipo de retorno de la función. Defecto: sys_refcursor
        :return: Lo que retorne la funcion
        """
        pass


class ConnectionOracle(Connection):
    def __init__(self, usr, pwd):
        super().__init__(cx_Oracle.connect(user=usr, password=pwd,
                                     dsn="localhost:1521/XEPDB1",
                                     encoding="UTF-8"))

    @staticmethod
    def getQueryFunction(func, tipo="sys_refcursor"):
        """
        Empaqueta el nombre de la funcion en un string para que la funcion pueda ser leida correctamente
        :param func: nombre funcion con sus parametros (si tiene)
        :param tipo: Tipo de retorno de la función. Defecto: sys_refcursor
        :return: Lo que retorne la funcion
        """
        return '''\
                     declare
                         l_examples {0};
                     begin
                         l_examples := {1};
                         dbms_sql.return_result(l_examples);
                     end;
                     '''.format(tipo, func)

    def execProcedure(self, proc, params=None):
        pass

    def execProcedureJson(self, param):
        pass


class ConnectionSql(Connection):
    def __init__(self):
        super().__init__(pyodbc.connect(r'Driver=SQL Server;Server=DESKTOP-59HG65S\SQLEXPRESS2017;'
                                        r'Database=Finanzas;User Id=jp;Password=jp;'))
        self.con.autocommit = False

    @staticmethod
    def processParams(params):
        newParams = ''
        if params is not None:
            newParams = ''
            for param in params:
                newParams += "'" + param + "', "
            newParams = newParams[0:len(newParams)-2]
        newParams += ';'

        return newParams

    def execProcedure(self, proc, params=None):
        params = ConnectionSql.processParams(params)
        self.cursor.execute("EXEC " + proc + params)

    def execFunction(self, func, params=None):
        params = ConnectionSql.processParams(params)
        self.cursor.execute("""
        declare @aux NVARCHAR(MAX);
        EXEC @aux = {0} {1}
        select @aux;
        """.format(func, params))






"""
Connection:
    ok
    nook
    execSelect
"""