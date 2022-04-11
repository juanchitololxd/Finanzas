import cx_Oracle
import pandas as pd



class ConnectionOracle:
    def __init__(self, usr, pwd):
        self.con = cx_Oracle.connect(user=usr, password=pwd,
                                     dsn="localhost:1521/XEPDB1",
                                     encoding="UTF-8")
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

    def execInsNoCommit(self, query):
        """
        Realiza un insert sin hacer commit
        :param query: consulta
        """
        print(query)
        self.cursor.execute(query)

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
        self.cursor.execute("ROLLBACK")
        print("ROLLBACK")

    def close(self):
        self.cursor.close()
        self.con.close()
        print("Conexion cerrada")

    def execSelect(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def execFunction(self, query):
        self.cursor.execute(query)

    def execProcedure(self, proc, params=None):
        if params is None:
            params = []
        self.cursor.callproc(proc, params)

    def getCursor(self):
        return self.cursor

    @staticmethod
    def getQueryFunctionFromPkg(pkg, func):
        """
        Empaqueta el nombre de la funcion en un string para que la funcion pueda ser leida correctamente
        :param func: nombre funcion con sus parametros (si tiene)
        :param pkg: nombre del paquete
        :return: Lo que retorne la funcion
        """
        return '''\
                    declare
                        l_examples sys_refcursor;
                    begin
                        l_examples := {0}.{1};
                        dbms_sql.return_result(l_examples);
                    end;
                    '''.format(pkg, func)

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

