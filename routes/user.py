from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
import bcrypt
from typing import List
from config.db import conn
from models.user import users, rol, vehiculos, bitacora, proyecto, gasolineras, log
from schemas.user_schema import User, UserCount, VehiculoCreate, VehiculoResponse, Bitacora, BitacoraResponse
from schemas.user_schema import  Rol, LogCreate, LogResponse, Proyectos, Gasolinera, LoginRequest
from sqlalchemy import func, select, insert, update, delete, join
from utils.auth import verify_password 

user = APIRouter()

# Función para encriptar la contraseña necesario
def encrypt_password(password: str) -> str:
    salt = bcrypt.gensalt()  # Genera un "salt" aleatorio
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)  # Hashea la contraseña
    return hashed_password.decode('utf-8')  # Devuelve el hash como string

# Función de login
@user.post("/login", tags=["users"], description="Login user") #okkkkkkk
def login(request: LoginRequest):
    try:
        # Realizar la consulta para obtener el usuario
        query = select(users).where(users.c.username == request.username)  # Usamos 'select' de SQLAlchemy
        user = conn.execute(query).fetchone()  # Ejecutamos la consulta y obtenemos el primer resultado
        
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Acceder a los valores de la tupla usando índices
        user_id = user[0]  # id_usuario está en la primera posición
        username = user[7]  # username está en la séptima posición (suponiendo que es el séptimo campo)
        password_hash = user[4]  # password está en la quinta posición (suponiendo que es el quinto campo)

        # Verificar la contraseña usando la función de hash
        if not verify_password(request.password, password_hash):  # Usamos el hash de la contraseña
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        
        # Si la contraseña es correcta, devuelve el usuario
        return {"id_usuario": user_id, "username": username}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Obtener el conteo de usuarios
@user.get("/users/count", tags=["users"], response_model=UserCount) #ok
def get_users_count():
    try:
        query = select(func.count()).select_from(users)
        result = conn.execute(query).scalar()
        return {"total": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener un usuario por su ID
@user.get("/users/{id}", tags=["users"], response_model=User, description="Get a single user by Id") #ok
def get_user(id: int):
    user_record = conn.execute(users.select().where(users.c.id_usuario == id)).first()
    if user_record is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_record

# Obtener todos los usuarios
@user.get("/users/", tags=["users"], response_model=List[User], description="Get all users") #ok
def get_all_users():
    return conn.execute(users.select()).fetchall()


# Crear un nuevo usuario
@user.post("/users/", tags=["users"], response_model=User, description="Create a new user")
def create_user(user: User):
    try:
        # Encriptamos la contraseña
        hashed_password = encrypt_password(user.password)
        
        new_user = {
            "nombre": user.nombre,
            "apellido": user.apellido,
            "password": hashed_password,  # Usamos la contraseña encriptada
            "id_rol": user.id_rol,
            "username": user.username,
            "created_at": datetime.now()
        }
        
        result = conn.execute(users.insert().values(new_user))
        conn.commit()
        return conn.execute(users.select().where(users.c.id_usuario == result.lastrowid)).first()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Actualizar un usuario por su ID
@user.put("/users/{id}", tags=["users"], response_model=User, description="Update a User by Id")
def update_user(id: int, user: User):
    existing_user = conn.execute(users.select().where(users.c.id_usuario == id)).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Si la contraseña fue proporcionada, encriptarla
    updated_values = {
        "nombre": user.nombre,
        "apellido": user.apellido,
        "id_rol": user.id_rol,
        "username": user.username
    }

    # Encriptar solo la contraseña si ha sido modificada
    if user.password:
        updated_values["password"] = encrypt_password(user.password)

    conn.execute(users.update().where(users.c.id_usuario == id).values(updated_values))
    conn.commit()
    return conn.execute(users.select().where(users.c.id_usuario == id)).first()

# Eliminar un usuario por su ID
@user.delete("/users/{id}", tags=["users"], status_code=status.HTTP_204_NO_CONTENT) #ok
def delete_user(id: int):
    result = conn.execute(users.delete().where(users.c.id_usuario == id))
    conn.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    return {"message": "Se eliminó el usuario", "id": id}

##################################################################################################################
# Crear un nuevo vehículo (si es necesario para tu aplicación)
@user.post("/vehiculos/", tags=["vehiculos"], description="Create a new vehicle") #ok
def create_vehicle(vehicle: VehiculoCreate):
    try:
        stmt = insert(vehiculos).values(
            modelo=vehicle.modelo,
            marca=vehicle.marca,
            placa=vehicle.placa,
            rendimiento=vehicle.rendimiento,
            galonaje=vehicle.galonaje,
            tipo_combustible=vehicle.tipo_combustible
        )
        conn.execute(stmt)
        conn.commit()

        new_vehicle_id = conn.execute(select(vehiculos.c.id_vehiculo).order_by(vehiculos.c.id_vehiculo.desc()).limit(1)).scalar_one()
        return {"message": "Vehicle created successfully", "vehicle_id": new_vehicle_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Obtener todos los vehículos (si es necesario para tu aplicación)
@user.get("/vehiculos/", tags=["vehiculos"], response_model=List[VehiculoResponse], description="Get all vehicles") #ok
def get_vehicles():
    try:
        stmt = select(
            vehiculos.c.id_vehiculo,
            vehiculos.c.modelo,
            vehiculos.c.marca,
            vehiculos.c.placa,
            vehiculos.c.rendimiento,
            vehiculos.c.galonaje,
            vehiculos.c.tipo_combustible
        )
        
        result = conn.execute(stmt).fetchall()
        vehicles = []
        for row in result:
            vehicle_data = {
                "id_vehiculo": row.id_vehiculo,  # Cambié 'id' a 'id_vehiculo'
                "modelo": row.modelo,
                "marca": row.marca,
                "placa": row.placa,
                "rendimiento": row.rendimiento,  # Cambié 'Rendimiento' a 'rendimiento'
                "galonaje": row.galonaje,        # Cambié 'Galonaje' a 'galonaje'
                "tipo_combustible": row.tipo_combustible
            }
            vehicles.append(vehicle_data)

        return vehicles
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Eliminar un vehículo por su ID #okk
@user.delete("/vehiculos/{id}", tags=["vehiculos"], status_code=status.HTTP_204_NO_CONTENT, description="Delete a vehicle by ID")
def delete_vehicle(id: int):
    try:
        # Construir la consulta para eliminar el vehículo
        stmt = vehiculos.delete().where(vehiculos.c.id_vehiculo == id)
        
        # Ejecutar la consulta
        result = conn.execute(stmt)
        conn.commit()
        
        # Verificar si se eliminó algún registro
        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
        
        return {"message": "Vehículo eliminado exitosamente", "vehicle_id": id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error eliminando el vehículo: {str(e)}")

# Actualizar un vehículo por su ID
@user.put("/vehiculos/{id}", tags=["vehiculos"], description="Update a vehicle by ID") #ok
def update_vehicle(id: int, vehicle: VehiculoCreate):
    try:
        # Construir la consulta para actualizar el vehículo
        stmt = vehiculos.update().where(vehiculos.c.id_vehiculo == id).values(
            modelo=vehicle.modelo,
            marca=vehicle.marca,
            placa=vehicle.placa,
            rendimiento=vehicle.rendimiento,
            galonaje=vehicle.galonaje,
            tipo_combustible=vehicle.tipo_combustible
        )
        
        # Ejecutar la consulta
        result = conn.execute(stmt)
        conn.commit()
        
        # Verificar si se actualizó algún registro
        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
        
        return {"message": "Vehículo actualizado exitosamente", "vehicle_id": id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error actualizando el vehículo: {str(e)}")


##################################################################################################################
# Crear un nuevo registro en la bitácora  -------------- probada y pasada
@user.post("/bitacora/", tags=["bitacora"], description="Create a new record in the bitacora") #no probada ojo faltan datos
def create_bitacora(record: Bitacora):
    try:
         # Preparamos la inserción de datos, incluyendo 'comentario' si es proporcionado
        stmt = insert(bitacora).values(
            created_at= datetime.now(),  # Añadimos 'created_at'
            comentario=record.comentario,   # Añadimos 'comentario' que es opcional
            km_inicial=record.km_inicial,
            km_final=record.km_final,
            num_galones=record.num_galones,
            costo=record.costo,
            tipo_gasolina=record.tipo_gasolina,
            id_usuario=record.id_usuario,
            id_vehiculo=record.id_vehiculo,
            id_gasolinera=record.id_gasolinera,
            id_proyecto=record.id_proyecto
        )
        conn.execute(stmt)
        conn.commit()

        new_record_id = conn.execute(select(bitacora.c.id_bitacora).order_by(bitacora.c.id_bitacora.desc()).limit(1)).scalar_one()
        return {"message": "Bitacora record created successfully", "record_id": new_record_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


#okokokokok
@user.get("/bitacora/", tags=["bitacora"], response_model=List[BitacoraResponse], description="Get all bitacora records with related data")
def get_bitacora():
    try:
        stmt = select(
            bitacora.c.id_bitacora,
            bitacora.c.created_at,
            bitacora.c.comentario,
            bitacora.c.km_inicial,
            bitacora.c.km_final,
            bitacora.c.num_galones,
            bitacora.c.costo,
            bitacora.c.tipo_gasolina,
            users.c.nombre.label("usuario"),  # Nombre del usuario
            vehiculos.c.modelo.label("vehiculo"),  # Modelo del vehículo
            gasolineras.c.nombre.label("gasolineras"),  # Corregir alias para gasolinera
            proyecto.c.nombre.label("proyecto")  # Nombre del proyecto
        ).join(users, bitacora.c.id_usuario == users.c.id_usuario) \
         .join(vehiculos, bitacora.c.id_vehiculo == vehiculos.c.id_vehiculo) \
         .join(gasolineras, bitacora.c.id_gasolinera == gasolineras.c.id_gasolinera) \
         .join(proyecto, bitacora.c.id_proyecto == proyecto.c.id_proyecto)

        result = conn.execute(stmt).fetchall()

        # Preparamos la lista de registros con los datos obtenidos
        records = []
        for row in result:
            record_data = {
                "id_bitacora": row.id_bitacora,
                "created_at": row.created_at,
                "comentario": row.comentario,
                "km_inicial": row.km_inicial,
                "km_final": row.km_final,
                "num_galones": row.num_galones,
                "costo": row.costo,
                "tipo_gasolina": row.tipo_gasolina,
                "usuario": row.usuario,  # Usuario como 'usuario'
                "vehiculo": row.vehiculo,  # Vehículo como 'vehiculo'
                "gasolineras": row.gasolineras,  # Gasolinera como 'gasolineras'
                "proyecto": row.proyecto  # Proyecto como 'proyecto'
            }
            records.append(record_data)

        return records

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving bitacora records: {str(e)}")

# Eliminar un registro de la bitácora por su ID
@user.delete("/bitacora/{id}", tags=["bitacora"], status_code=status.HTTP_204_NO_CONTENT, description="Delete a record from the bitacora by ID")
def delete_bitacora(id: int):
    try:
        # Preparamos la consulta DELETE
        stmt = bitacora.delete().where(bitacora.c.id_bitacora == id)
        result = conn.execute(stmt)
        conn.commit()
        
        # Comprobamos si se eliminó algún registro
        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de bitácora no encontrado")

        return {"message": "Registro de bitácora eliminado exitosamente", "id": id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error eliminando el registro de bitácora: {str(e)}")

# Actualizar un registro en la bitácora -------------- Adaptado y funcional OK
@user.put("/bitacora/{id}", tags=["bitacora"], description="Update an existing record in the bitacora")
def update_bitacora(id: int, record: Bitacora):
    try:
        # Preparamos la actualización de datos
        stmt = (
            update(bitacora)
            .where(bitacora.c.id_bitacora == id)
            .values(
                comentario=record.comentario,  # 'comentario' es opcional
                km_inicial=record.km_inicial,
                km_final=record.km_final,
                num_galones=record.num_galones,
                costo=record.costo,
                tipo_gasolina=record.tipo_gasolina,
                id_usuario=record.id_usuario,
                id_vehiculo=record.id_vehiculo,
                id_gasolinera=record.id_gasolinera,
                id_proyecto=record.id_proyecto
            )
        )
        result = conn.execute(stmt)
        conn.commit()

        # Verificar si se actualizó algún registro
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro de bitácora no encontrado.")

        return {"message": "Registro de bitácora actualizado exitosamente", "record_id": id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error actualizando el registro de bitácora: {str(e)}")

##################################################################################################################
# Crear un rol  okkkkk
@user.post("/roles/", tags=["roles"], response_model=Rol, status_code=status.HTTP_201_CREATED)
def create_role(role: Rol):
    try:
        stmt = insert(rol).values(descripcion=role.descripcion)
        result = conn.execute(stmt)
        conn.commit()
        
        # Recuperar el ID recién creado
        new_role_id = result.lastrowid
        created_role = conn.execute(select(rol).where(rol.c.id_rol == new_role_id)).fetchone()
        return Rol(id_rol=created_role.id_rol, descripcion=created_role.descripcion)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando el rol: {str(e)}")


# Leer todos los roles
@user.get("/roles/", tags=["roles"], response_model=list[Rol]) #ok
def get_roles():
    try:
        result = conn.execute(select(rol)).fetchall()
        return [Rol(id_rol=row.id_rol, descripcion=row.descripcion) for row in result]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener los roles: {str(e)}")


# Leer un rol por ID
@user.get("/roles/{id_rol}", tags=["roles"], response_model=Rol) #ok
def get_role_by_id(id_rol: int):
    try:
        result = conn.execute(select(rol).where(rol.c.id_rol == id_rol)).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        return Rol(id_rol=result.id_rol, descripcion=result.descripcion)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener el rol: {str(e)}")


# Actualizar un rol
@user.put("/roles/{id_rol}", tags=["roles"], response_model=Rol) #ok
def update_role(id_rol: int, role: Rol):
    try:
        stmt = update(rol).where(rol.c.id_rol == id_rol).values(descripcion=role.descripcion)
        result = conn.execute(stmt)
        conn.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        
        updated_role = conn.execute(select(rol).where(rol.c.id_rol == id_rol)).fetchone()
        return Rol(id_rol=updated_role.id_rol, descripcion=updated_role.descripcion)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error actualizando el rol: {str(e)}")


# Eliminar un rol
@user.delete("/roles/{id_rol}", tags=["roles"], status_code=status.HTTP_204_NO_CONTENT) #ok
def delete_role(id_rol: int):
    try:
        stmt = delete(rol).where(rol.c.id_rol == id_rol)
        result = conn.execute(stmt)
        conn.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        return {"message": f"Rol con id {id_rol} eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error eliminando el rol: {str(e)}")
    
##################################################################################################################
# Crear un registro de log
#ojo en este tenemos que ver el disparador para cuando se haga lo del login
@user.post("/logs/", tags=["logs"], response_model=LogResponse, status_code=status.HTTP_201_CREATED)
def create_log(log_entry: LogCreate):
    try:
        stmt = insert(log).values(
            descripcion=log_entry.descripcion,
            id_usuario=log_entry.id_usuario,
            created_at=datetime.now()  # Se establece el timestamp actual
        )
        result = conn.execute(stmt)
        conn.commit()

        # Recuperar el ID recién creado
        new_log_id = result.lastrowid
        created_log = conn.execute(select(log).where(log.c.id_log == new_log_id)).fetchone()
        return LogResponse(
            id_log=created_log.id_log,
            created_at=created_log.created_at,
            descripcion=created_log.descripcion,
            id_usuario=created_log.id_usuario
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando el log: {str(e)}")


# Leer todos los registros de log
@user.get("/logs/", tags=["logs"], response_model=list[LogResponse])
def get_logs():
    try:
        result = conn.execute(select(log)).fetchall()
        return [
            LogResponse(
                id_log=row.id_log,
                created_at=row.created_at,
                descripcion=row.descripcion,
                id_usuario=row.id_usuario
            ) for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener los logs: {str(e)}")


# Leer un log por ID
@user.get("/logs/{id_log}", tags=["logs"], response_model=LogResponse)
def get_log_by_id(id_log: int):
    try:
        result = conn.execute(select(log).where(log.c.id_log == id_log)).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Log no encontrado")
        return LogResponse(
            id_log=result.id_log,
            created_at=result.created_at,
            descripcion=result.descripcion,
            id_usuario=result.id_usuario
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al obtener el log: {str(e)}")

# Actualizar un log
@user.put("/logs/{id_log}", tags=["logs"], response_model=LogResponse)
def update_log(id_log: int, log_entry: LogCreate):
    try:
        stmt = update(log).where(log.c.id_log == id_log).values(
            descripcion=log_entry.descripcion,
            id_usuario=log_entry.id_usuario
        )
        result = conn.execute(stmt)
        conn.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Log no encontrado")
        
        updated_log = conn.execute(select(log).where(log.c.id_log == id_log)).fetchone()
        return LogResponse(
            id_log=updated_log.id_log,
            created_at=updated_log.created_at,
            descripcion=updated_log.descripcion,
            id_usuario=updated_log.id_usuario
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error actualizando el log: {str(e)}")


# Eliminar un log
@user.delete("/logs/{id_log}", tags=["logs"], status_code=status.HTTP_204_NO_CONTENT)
def delete_log(id_log: int):
    try:
        stmt = delete(log).where(log.c.id_log == id_log)
        result = conn.execute(stmt)
        conn.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Log no encontrado")
        return {"message": f"Log con id {id_log} eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error eliminando el log: {str(e)}")
    
    
##################################################################################################################
#agg proyecto
@user.post("/proyectos/", tags=["proyectos"], response_model=Proyectos, description="Create a new project") #okk
def create_proyecto(proyecto_data: Proyectos):
    try:
        # Crear el nuevo proyecto como un diccionario de datos
        new_proyecto = {
            "nombre": proyecto_data.nombre,
            "direccion": proyecto_data.direccion,
            "activo": proyecto_data.activo,
            "created_at": datetime.now()
        }

        # Ejecutar la inserción en la base de datos usando la tabla 'proyecto'
        result = conn.execute(proyecto.insert().values(new_proyecto))
        conn.commit()

        # Obtener y devolver el proyecto recién creado
        # Usamos select() para obtener el último proyecto insertado
        return conn.execute(proyecto.select().where(proyecto.c.id_proyecto == result.lastrowid)).fetchone()
    
    except Exception as e:
        conn.rollback()  # Revertir si ocurre un error
        raise HTTPException(status_code=400, detail=str(e))
    
#por id
@user.get("/proyectos/{id_proyecto}", response_model=Proyectos, tags=["proyectos"]) #ok
def get_proyecto(id_proyecto: int):
    proyecto_data = conn.execute(
        select(proyecto).where(proyecto.c.id_proyecto == id_proyecto)
    ).mappings().first()

    if not proyecto_data:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    return proyecto_data

#all proyectos
@user.get("/proyectos/", response_model=List[Proyectos], tags=["proyectos"]) #ok
def get_all_proyectos():
    proyectos = conn.execute(select(proyecto)).mappings().all()
    return proyectos

#actualizar 
@user.put("/proyectos/{id_proyecto}", response_model=Proyectos, tags=["proyectos"]) #ok
def update_proyecto(id_proyecto: int, proyecto_update: Proyectos):
    stmt = (
        update(proyecto)
        .where(proyecto.c.id_proyecto == id_proyecto)
        .values(
            nombre=proyecto_update.nombre,
            direccion=proyecto_update.direccion,
            activo=proyecto_update.activo,
        )
    )
    try:
        result = conn.execute(stmt)
        conn.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")

        proyecto_actualizado = conn.execute(
            select(proyecto).where(proyecto.c.id_proyecto == id_proyecto)
        ).mappings().first()

        return proyecto_actualizado
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error actualizando proyecto: {str(e)}")

#delete
@user.delete("/proyectos/{id_proyecto}", tags=["proyectos"]) #ok
def delete_proyecto(id_proyecto: int):
    stmt = delete(proyecto).where(proyecto.c.id_proyecto == id_proyecto)
    try:
        result = conn.execute(stmt)
        conn.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")

        return {"message": "Proyecto eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error eliminando proyecto: {str(e)}")

##################################################################################################################
#post gasolinera
#ok
@user.post("/gasolineras/", tags=["gasolineras"], response_model=Gasolinera, description="Create a new gas station")
def create_gasolinera(gasolinera_data: Gasolinera):
    try:
        # Crear el nuevo gasolinera como un diccionario de datos
        new_gasolinera = {
            "nombre": gasolinera_data.nombre,
            "direccion": gasolinera_data.direccion,
            "created_at": datetime.now()
        }

        # Ejecutar la inserción en la base de datos
        result = conn.execute(gasolineras.insert().values(new_gasolinera))
        conn.commit()

        # Obtener y devolver la gasolinera recién creada
        return conn.execute(gasolineras.select().where(gasolineras.c.id_gasolinera == result.lastrowid)).fetchone()
    
    except Exception as e:
        conn.rollback()  # Revertir si ocurre un error
        raise HTTPException(status_code=400, detail=str(e))
    
#leer gas
@user.get("/gasolineras/", response_model=List[Gasolinera], tags=["gasolineras"], description="Get all gas stations") #ok
def get_all_gasolineras():
    try:
        # Ejecutar consulta para obtener todas las gasolineras
        gasolineras_list = conn.execute(select(gasolineras)).fetchall()
        return gasolineras_list
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
#gas por id
#ok
@user.get("/gasolineras/{id_gasolinera}", response_model=Gasolinera, tags=["gasolineras"], description="Get a gas station by ID")
def get_gasolinera(id_gasolinera: int):
    try:
        # Ejecutar consulta para obtener la gasolinera por ID
        gasolinera = conn.execute(gasolineras.select().where(gasolineras.c.id_gasolinera == id_gasolinera)).fetchone()
        
        if not gasolinera:
            raise HTTPException(status_code=404, detail="Gasolinera not found")
        
        return gasolinera
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#actualizar datos de gas
#ok
@user.put("/gasolineras/{id_gasolinera}", response_model=Gasolinera, tags=["gasolineras"], description="Update a gas station")
def update_gasolinera(id_gasolinera: int, gasolinera_data: Gasolinera):
    try:
        # Crear el diccionario con los nuevos valores
        update_data = {
            "nombre": gasolinera_data.nombre,
            "direccion": gasolinera_data.direccion,
        }

        # Ejecutar la actualización
        result = conn.execute(gasolineras.update().where(gasolineras.c.id_gasolinera == id_gasolinera).values(update_data))
        conn.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Gasolinera not found")
        
        # Obtener y devolver la gasolinera actualizada
        updated_gasolinera = conn.execute(gasolineras.select().where(gasolineras.c.id_gasolinera == id_gasolinera)).fetchone()
        return updated_gasolinera

    except Exception as e:
        conn.rollback()  # Revertir si ocurre un error
        raise HTTPException(status_code=400, detail=str(e))

#eliminar esta gas:
#ok
@user.delete("/gasolineras/{id_gasolinera}", tags=["gasolineras"], description="Delete a gas station")
def delete_gasolinera(id_gasolinera: int):
    try:
        # Ejecutar la eliminación de la gasolinera
        result = conn.execute(gasolineras.delete().where(gasolineras.c.id_gasolinera == id_gasolinera))
        conn.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Gasolinera no se encontro")
        
        return {"detail": "Gasolinera eliminada"}
    
    except Exception as e:
        conn.rollback()  # Revertir si ocurre un error
        raise HTTPException(status_code=400, detail=str(e))
