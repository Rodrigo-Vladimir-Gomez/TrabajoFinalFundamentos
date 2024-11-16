from sqlalchemy import create_engine, MetaData
#Creamos la conexion ala base de datos
engine=create_engine("mysql://rodrigo:wL0*dJ5*kP9:gC8*@us-east1-001.proxy.kinsta.app:30883/pruebagas")
#creamos la metadata para la creacion de los datos
meta=MetaData()
#almacenamos la conexion para utilizarla
conn=engine.connect()
