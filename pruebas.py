from dominio.connection import  ConnectionSql, ConnectionOracle

sql = ConnectionSql()

"""
for i in sql.execSelect("SELECT * FROM COMPRAS"):
    print(i) BIEN para selects"""
#sql.execFunction("select dbo.getSaldos(3) AS NVARCHAR")
aux = []
x = sql.execSelect("EXEc getCompras 2,2,2; ")[0][0]
print(type(x))

"""
for i in sql.execSelect(
    'EXEC  getCompras 2,2,2;')
   print(i)
"""





