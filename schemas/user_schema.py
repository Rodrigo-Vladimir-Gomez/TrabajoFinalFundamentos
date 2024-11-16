from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class LoginRequest(BaseModel):
    username: str
    password: str

# Modelo para la tabla de Roles (Rol)
class Rol(BaseModel):
    id_rol: Optional[int] = None
    descripcion: str

    class Config:
        from_attributes = True  # Cambié 'orm_mode' a 'from_attributes'

# Modelo para la tabla de Usuarios
class User(BaseModel):
    id_usuario: Optional[int] = None
    created_at: Optional[datetime] = None
    nombre: str
    apellido: str
    password: str
    id_rol: Optional[int] = None
    activo: bool = False
    username: str

    # Relación con el rol
    rol: Optional['Rol'] = None  # Usar comillas para evitar problemas de referencia circular

    class Config:
        from_attributes = True  # Cambié 'orm_mode' a 'from_attributes'

# Modelo para la tabla de Vehículos
class Vehiculo(BaseModel):
    id_vehiculo: Optional[int] = None
    created_at: Optional[datetime] = None
    modelo: str
    marca: str
    placa: str
    rendimiento: Optional[str] = None
    galonaje: Optional[float] = None
    tipo_combustible: str

    class Config:
        from_attributes = True  # Cambié 'orm_mode' a 'from_attributes'

# Modelo para la tabla de Gasolineras
class Gasolinera(BaseModel):
    id_gasolinera: Optional[int] = None
    created_at: Optional[datetime] = None
    nombre: str
    direccion: str

    class Config:
        from_attributes = True  # Cambié 'orm_mode' a 'from_attributes'

# Modelo para la tabla de Proyecto
class Proyectos(BaseModel):
    id_proyecto: Optional[int] = None
    created_at: Optional[datetime] = None
    nombre: str
    direccion: str
    activo: bool = False

    class Config:
        from_attributes = True  # Cambié 'orm_mode' a 'from_attributes'

# Modelo para la tabla de Bitacora
class Bitacora(BaseModel):
    id_bitacora: Optional[int] = None
    created_at: Optional[datetime] = None
    comentario: Optional[str] = None
    km_inicial: int
    km_final: int
    num_galones: float
    costo: float
    tipo_gasolina: str
    id_usuario: int
    id_vehiculo: int
    id_gasolinera: int
    id_proyecto: int

    # Relación con el Usuario, Vehículo, Gasolinera y Proyecto
    usuario: Optional[User] = None
    vehiculo: Optional[Vehiculo] = None
    gasolinera: Optional[Gasolinera] = None
    proyecto: Optional[Proyectos] = None

    class Config:
        from_attributes = True  # Cambié 'orm_mode' a 'from_attributes'

# Clase de respuesta de Bitacora, con las relaciones necesarias
class BitacoraResponse(BaseModel):
    id_bitacora: int
    created_at: datetime
    comentario: Optional[str] = None
    km_inicial: int
    km_final: int
    num_galones: float
    costo: float
    tipo_gasolina: str
    usuario: Optional[str] = None  # Nombre del usuario
    vehiculo: Optional[str] = None  # Modelo del vehículo
    gasolinera: Optional[str] = None  # Nombre de la gasolinera
    proyecto: Optional[str] = None  # Nombre del proyecto

    class Config:
        from_attributes = True

# Modelo para contar los usuarios totales
class UserCount(BaseModel):
    total: int

# Modelo de creación de un nuevo Vehículo
class VehiculoCreate(BaseModel):
    modelo: str
    marca: str
    placa: str
    rendimiento: Optional[str] = None
    galonaje: Optional[float] = None
    tipo_combustible: str

    class Config:
        from_attributes = True  # Cambié 'orm_mode' a 'from_attributes'

# Modelo de respuesta para un Vehículo
class VehiculoResponse(BaseModel):
    id_vehiculo: int
    modelo: str
    marca: str
    placa: str
    rendimiento: Optional[str] = None
    galonaje: Optional[float] = None
    tipo_combustible: str

    class Config:
        from_attributes = True  # Cambié 'orm_mode' a 'from_attributes'

# Modelo para crear un nuevo Log de actividad (por ejemplo, inicio de sesión)
class LogCreate(BaseModel):
    descripcion: str
    id_usuario: int

    class Config:
        from_attributes = True  # Cambié 'orm_mode' a 'from_attributes'

# Respuesta para el Log
class LogResponse(BaseModel):
    id_log: int
    created_at: Optional[datetime] = None
    descripcion: str
    id_usuario: int

    class Config:
        from_attributes = True  # Cambié 'orm_mode' a 'from_attributes'


