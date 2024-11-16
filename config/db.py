from sqlalchemy import create_engine, MetaData
#Creamos la conexion ala base de datos
engine=create_engine("postgresql://root:XItt9pnTL9HRKHNYMsvr53iVaSgcNuK4@dpg-csrvc3btq21c739pu8v0-a.oregon-postgres.render.com/pruebagas_k20d")
#creamos la metadata para la creacion de los datos
meta=MetaData()
#almacenamos la conexion para utilizarla
conn=engine.connect()