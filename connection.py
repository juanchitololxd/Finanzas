import cx_Oracle
import pandas as pd

class Connection:
    def __init__(self):
        self.con = cx_Oracle.connect(user="jp", password="jp2",
                                     dsn="localhost:1521/XEPDB1",
                                     encoding="UTF-8")
        print("conexion establecida")
        self.cursor = self.con.cursor()


    def execSelect(self, query):
        return self.cursor.execute(query)

    def execSelectPd(self, query):
        return pd.read_sql(query, con=self.con)

    def execInsNoCommit(self, query):
        print(query)
        self.cursor.execute(query)

    def okay(self):
        self.con.commit()
        print("COMMIT REALIZADO!")

    def NoOkay(self):
        self.execOther("ROLLBACK")

    def execOther(self, query):
        print(query)
        self.cursor.execute(query)
        self.con.commit()
        print("commit realizado")

    def close(self):
        self.cursor.close()
        self.con.close()
        print("Conexion cerrada")

