from sqlalchemy import create_engine, MetaData
#Creamos la conexion ala base de datos
engine=create_engine("postgresql://root:LAx5J73uFh3lcIjLbvS6ZcOPM3oX53Me@dpg-css0jiq3esus739gbbf0-a.oregon-postgres.render.com/gasolineria")
#creamos la metadata para la creacion de los datos
meta=MetaData()
#almacenamos la conexion para utilizarla
conn=engine.connect()
