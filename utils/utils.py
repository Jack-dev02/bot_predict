import random
from datetime import timedelta, datetime
from config.config import Envs, BOT_OWNER_ID
from data.data_handler import temp_codes_collection, users_collection
import pytz

# --------------------- Funciones de gestión de códigos temporales ---------------------

def generate_temp_code():
    code = ''.join(random.choices('//*-+ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@$%&?¡!#', k=16))
    return code

def parse_time(duration_str):
    unit = duration_str[-1]
    amount = int(duration_str[:-1])
    if unit == 'm':
        return timedelta(minutes=amount)
    elif unit == 'h':
        return timedelta(hours=amount)
    elif unit == 'd':
        return timedelta(days=amount)
    else:
        raise ValueError("Unidad de tiempo no válida...")

# --------------------- Funciones de gestión de permisos, usuarios y eliminar códigos expirados ---------------------
def has_permission(user_id):
    print(f"Verificando permisos para el usuario {user_id}")
    if user_id == BOT_OWNER_ID:
        print(f"{Envs.Owner} es el dueño del bot, tiene permiso.")
        return True

    user = users_collection.find_one({"user_id": user_id})
    if user and user.get("has_access"):
        temp_code_data = temp_codes_collection.find_one({"user_id": user_id})
        if temp_code_data:
            expiration_date = temp_code_data["expiration"]
            if expiration_date.tzinfo is None:
                expiration_date = expiration_date.replace(tzinfo=pytz.utc)

            utc_time_now = datetime.now(pytz.utc)

            if utc_time_now > expiration_date:
                # users_collection.delete_one({"user_id": user_id}) #Elimina el usuario y el código
                users_collection.update_one({"user_id": user_id}, {"$set": {"has_access": False}})
                temp_codes_collection.delete_one({"user_id": user_id})
                print("Permiso revocado y código expirado eliminado.")
                return False
            else:
                return True
        else:
            return True 

    return False
