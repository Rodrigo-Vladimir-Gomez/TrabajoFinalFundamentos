from sqlalchemy import Table, Column, Integer, String, Boolean, Text, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from config.db import meta, engine

# Tabla de roles (rol)
rol = Table("rol", meta,
    Column("id_rol", Integer, primary_key=True, autoincrement=True),
    Column("descripcion", Text, nullable=False)
)

# Tabla de usuarios (usuarios)
users = Table("usuarios", meta,
    Column("id_usuario", Integer, primary_key=True, autoincrement=True),
    Column("created_at", DateTime, default=func.current_timestamp(), nullable=False),  # Se usa default aquí
    Column("nombre", String(50), nullable=False),
    Column("apellido", String(50), nullable=False),
    Column("password", String(255), nullable=False),
    Column("id_rol", Integer, ForeignKey("rol.id_rol")),
    Column("activo", Boolean, default=False),
    Column("username", String(30), unique=True),
)

# Tabla de vehículos (vehiculos)
vehiculos = Table("vehiculos", meta,
    Column("id_vehiculo", Integer, primary_key=True, autoincrement=True),
    Column("created_at", DateTime, default=func.current_timestamp(), nullable=False),  # Se usa default aquí
    Column("modelo", String(50), nullable=False),
    Column("marca", String(50), nullable=False),
    Column("placa", String(30), unique=True, nullable=False),
    Column("rendimiento", String(30)),
    Column("galonaje", Float),
    Column("tipo_combustible", String(25), nullable=False),
)

# Tabla de logs (log)
log = Table("log", meta,
    Column("id_log", Integer, primary_key=True, autoincrement=True),
    Column("created_at", DateTime, default=func.current_timestamp(), nullable=False),  # Se usa default aquí
    Column("descripcion", Text, nullable=False),
    Column("id_usuario", Integer, ForeignKey("usuarios.id_usuario")),
)

# Tabla de proyectos (proyecto)
proyecto = Table("proyecto", meta,
    Column("id_proyecto", Integer, primary_key=True, autoincrement=True),
    Column("created_at", DateTime, default=func.current_timestamp(), nullable=False),  # Se usa default aquí
    Column("nombre", String(50), nullable=False),
    Column("direccion", String(60), nullable=False),
    Column("activo", Boolean, default=False),
)

# Tabla de gasolineras (gasolineras)
gasolineras = Table("gasolineras", meta,
    Column("id_gasolinera", Integer, primary_key=True, autoincrement=True),
    Column("created_at", DateTime, default=func.current_timestamp(), nullable=False),  # Se usa default aquí
    Column("nombre", String(50), nullable=False),
    Column("direccion", String(60), nullable=False),
)

# Tabla de bitácoras (bitacora)
bitacora = Table("bitacora", meta,
    Column("id_bitacora", Integer, primary_key=True, autoincrement=True),
    Column("created_at", DateTime, default=func.current_timestamp(), nullable=False),  # Se usa default aquí
    Column("comentario", Text),
    Column("km_inicial", Integer, nullable=False),
    Column("km_final", Integer, nullable=False),
    Column("num_galones", Float, nullable=False),
    Column("costo", Float, nullable=False),
    Column("tipo_gasolina", String(30), nullable=False),
    Column("id_usuario", Integer, ForeignKey("usuarios.id_usuario")),
    Column("id_vehiculo", Integer, ForeignKey("vehiculos.id_vehiculo")),
    Column("id_gasolinera", Integer, ForeignKey("gasolineras.id_gasolinera")),
    Column("id_proyecto", Integer, ForeignKey("proyecto.id_proyecto")),
)

# Crear las tablas en la base de datos
meta.create_all(engine)
