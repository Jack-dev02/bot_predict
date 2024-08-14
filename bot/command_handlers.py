import threading
from telegram import Update
from telegram.ext import CallbackContext
from data.model_manager import load_model, compare_teams, train_model
from data.data_handler import db, collection, temp_codes_collection, users_collection
from utils.utils import has_permission, generate_temp_code, parse_time
from config.config import Envs, BOT_OWNER_ID
from datetime import datetime, timedelta
from config.logger_config import logger
import pytz
import os

async def start(update: Update, _: CallbackContext) -> None:
    welcome_message = "Hola, bienvenido al bot de predicción de resultados deportivos. Usa /help para ver los comandos disponibles."
    await update.message.reply_text(welcome_message)

async def help(update: Update, _: CallbackContext) -> None:
    help_text = """
    Bienvenido al bot de predicción de deportes. Aquí tienes los comandos disponibles:
    
    /start - Inicia el bot
    /help - Muestra este mensaje de ayuda
    /compare - Compara dos equipos y predice el resultado
    /train - Entrena el modelo con los datos actuales
    /adddata - Agrega datos de un partido al modelo
    /deletedata - Elimina todos los datos de los partidos del modelo
    /getcode - Genera un código de acceso temporal (Solo admin)
    /redeemcode - Redime un código de acceso temporal

    Ejemplo: /compare Barcelona,8,4,3,3;RealMadrid,9,4,3,3
    Ejemplo: /adddata 4,2,1,3,1,2,1
    """
    await update.message.reply_text(help_text)

async def compare(update: Update, _: CallbackContext) -> None:
    user_id = update.effective_user.id
    print(f"Usuario {user_id} ha ejecutado el comando /compare")

    if not has_permission(user_id):
        await update.message.reply_text(f"No tienes permiso para usar este comando, contacta al Administrador {Envs.Owner}.")
        return

    try:
        # 1. Manejo de errores más robusto
        if not update.message or not update.message.text:
            raise ValueError("Error: No se proporcionó un mensaje válido.")

        user_input = update.message.text.split('/compare', 1)[1].strip()
        
        # 1.1. Carga del modelo
        model = load_model(user_id)

        # 2. Separación de equipos y datos (adaptado para el nuevo formato)
        team_data = [
            dict(zip(["nombre", "goles", "ganadas", "perdidas","empates"], team.split(',')))
            for team in user_input.split(';')
            if team.strip()
        ] 

        # 3. Validación mejorada y mensajes de error descriptivos
        if len(team_data) != 2:
            raise ValueError("Error: Debes proporcionar exactamente dos equipos.")

        for team in team_data:
            if any(key not in team for key in ["nombre", "goles", "ganadas", "perdidas","empates"]):
                raise ValueError("Error: Faltan datos en uno o ambos equipos.")

            for key in ["goles", "ganadas", "perdidas"]:
                if not team[key].isdigit():
                    raise ValueError(f"Error: El valor de '{key}' en el equipo '{team['nombre']}' debe ser un número entero.")
        

        # Extraer nombres y datos
        team_names = [team["nombre"] for team in team_data]
        team_data = [[int(team[key]) for key in ["goles", "ganadas", "perdidas","empates"]] for team in team_data]
        
        total_partidos = sum([sum(values[:3]) for values in team_data])  # Solo sumar goles, ganadas y perdidas
        porcentaje_goles_equipo1 = (team_data[0][0] / total_partidos) * 100 if total_partidos > 0 else 0
        porcentaje_goles_equipo2 = (team_data[1][0] / total_partidos) * 100 if total_partidos > 0 else 0

        result, prediction_proba = compare_teams(team_data[0], team_data[1], model)
        
        # Manejo de errores en la predicción
        # if result is None:
        #     raise ValueError("No tienes suficientes datos para hacer una predicción. Agrega más datos con /adddata y luego entrena el modelo con /train.")
        
        if result is None:
            await update.message.reply_text("No tienes suficientes datos para hacer una predicción. Agrega más datos con /adddata y luego entrena el modelo con /train.")
            return

        result_text = f"{team_names[0]} ganará ✅" if result == 1 else f"{team_names[1]} ganará ✅" if result == 0 else "Empate 🟰"


        response_text = f"""Comparación entre {team_names[0]} y {team_names[1]}:

- - - - - - - - - - - - - - - - - - - - -
Resultado: {result_text}
- - - - - - - - - - - - - - - - - - - - -
Probabilidades {team_names[0]} - ↯ 
Victoria: {prediction_proba[1]:.2%} ✅
Derrota:  {prediction_proba[0]:.2%} ❌
Empate:   {prediction_proba[2]:.2%} 🟰
Porcentaje de goles: {porcentaje_goles_equipo1:.2f}% ⚽
- - - - - - - - - - - - - - - - - - - - -
Probabilidades {team_names[1]} - ↯ 
Victoria: {prediction_proba[0]:.2%} ✅
Derrota:  {prediction_proba[1]:.2%} ❌
Empate:   {prediction_proba[2]:.2%} 🟰
Porcentaje de goles: {porcentaje_goles_equipo2:.2f}% ⚽
- - - - - - - - - - - - - - - - - - - - -
Check by {user_id}
Dev by - ↯ {Envs.Onwer}"""

        await update.message.reply_text(response_text)
    except IndexError:
        await update.message.reply_text('Por favor, usa el formato: /compare equipo1_nombre, equipo1_goles, equipo1_veces_ganadas, equipo1_veces_perdidas,equipo1_veces_empatados; equipo2_nombre, equipo2_goles, equipo2_veces_ganadas, equipo2_veces_perdidas,equipo2_veces_empatados')
        await update.message.reply_text('Por favor, usa el formato: /compare equipo1_nombre, equipo1_goles, equipo1_veces_ganadas, equipo1_veces_perdidas,equipo1_veces_empatados; equipo2_nombre, equipo2_goles, equipo2_veces_ganadas, equipo2_veces_perdidas,equipo2_veces_empatados')
        await update.message.reply_text('Por favor, usa el formato: /compare equipo1_nombre, equipo1_goles, equipo1_veces_ganadas, equipo1_veces_perdidas,equipo1_veces_empatados; equipo2_nombre, equipo2_goles, equipo2_veces_ganadas, equipo2_veces_perdidas,equipo2_veces_empatados')
        await update.message.reply_text('Por favor, usa el formato: /compare equipo1_nombre, equipo1_goles, equipo1_veces_ganadas, equipo1_veces_perdidas,equipo1_veces_empatados; equipo2_nombre, equipo2_goles, equipo2_veces_ganadas, equipo2_veces_perdidas,equipo2_veces_empatados')
        await update.message.reply_text('Por favor, usa el formato: /compare equipo1_nombre, equipo1_goles, equipo1_veces_ganadas, equipo1_veces_perdidas,equipo1_veces_empatados; equipo2_nombre, equipo2_goles, equipo2_veces_ganadas, equipo2_veces_perdidas,equipo2_veces_empatados')
    except ValueError as e:
        await update.message.reply_text(f'Error en el formato de entrada: {e}. Por favor, usa el formato: /compare equipo1_nombre, equipo1_goles, equipo1_veces_ganadas, equipo1_veces_perdidas,equipo1_veces_empatados; equipo2_nombre, equipo2_goles, equipo2_veces_ganadas, equipo2_veces_perdidas,equipo2_veces_empatados')
    except Exception as e:
        logger.error(f"Error inesperado en la comparación: {e}")
        await update.message.reply_text("Lo siento, hubo un error al procesar tu solicitud.")

# Comando para añadir datos a la base de datos
async def adddata(update: Update, _: CallbackContext) -> None:
    user_id = update.effective_user.id
    print(f"Usuario {user_id} ha ejecutado el comando /adddata")

    if not has_permission(user_id):
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return

    try:
        user_input = update.message.text.split(maxsplit=1)[1].strip()
        user_input = [x.strip() for x in user_input.split(',')]  
        
        if len(user_input) != 7:
            raise ValueError("Número incorrecto de argumentos. Usa: /adddata goles1, veces_ganadas1, veces_perdidas1, goles2, veces_ganadas2, veces_perdidas2, resultado")
        
        # Extraer datos
        goals1, wins1, losses1 = int(user_input[0]), int(user_input[1]), int(user_input[2])
        goals2, wins2, losses2 = int(user_input[3]), int(user_input[4]), int(user_input[5])
        result = int(user_input[6])

        new_data = {
            "team1_features": [goals1, wins1, losses1],
            "team2_features": [goals2, wins2, losses2],
            "result": result
        }

        collection_name = f'matches_{user_id}'
        user_collection = db[collection_name]
        user_collection.insert_one(new_data) 

        collection.insert_one(new_data)
        await update.message.reply_text("Datos añadidos exitosamente. Por favor, entrena el modelo nuevamente.")
    except IndexError:
        await update.message.reply_text('Por favor, usa el formato: /adddata goles1, veces_ganadas1, veces_perdidas1, goles2, veces_ganadas2, veces_perdidas2, resultado')
    except ValueError as e:
        await update.message.reply_text(f'Error en el formato de entrada: {e}. Por favor, usa el formato: /adddata goles1, veces_ganadas1, veces_perdidas1, goles2, veces_ganadas2, veces_perdidas2, resultado')
    except Exception as e:
        logger.error(f"Error inesperado al agregar datos: {e}")
        await update.message.reply_text("Lo siento, hubo un error al procesar tu solicitud.")

# Comando para eliminar todos los datos del usuario de la base de datos
async def deletedata(update: Update, _: CallbackContext) -> None:
    user_id = update.effective_user.id
    print(f"Usuario {user_id} ha ejecutado el comando /deletedata")

    if not has_permission(user_id):
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return

    try:
        collection_name = f'matches_{user_id}'
        user_collection = db[collection_name]

        # Eliminar todos los documentos de la colección del usuario
        result = user_collection.delete_many({})
        print(result)

        if result.deleted_count > 0:
            await update.message.reply_text(f"Se han eliminado {result.deleted_count} registros de tu base de datos.")
        else:
            await update.message.reply_text("Tu base de datos ya está vacía.")

        # Opcional: Eliminar el modelo del usuario si existe
        model_path = f'model_{user_id}.pkl'
        if os.path.exists(model_path):
            os.remove(model_path)
            await update.message.reply_text("También se ha eliminado tu modelo entrenado.")

    except Exception as e:
        logger.error(f"Error inesperado al eliminar datos: {e}")
        await update.message.reply_text("Lo siento, hubo un error al procesar tu solicitud.")

# Comando para entrenar el modelo
async def train(update: Update, _: CallbackContext) -> None:
    user_id = update.effective_user.id
    print(f"Usuario {user_id} ha ejecutado el comando /train")

    if not has_permission(user_id):
        await update.message.reply_text(f"No tienes permiso para usar este comando, contacta al Administrador {Envs.Owner}.")
        return   
    global model  # Asegúrate de modificar el modelo global

    model = train_model(user_id)

    if model is None:  # Si no se pudo entrenar el modelo
        await update.message.reply_text("No tienes suficientes datos para entrenar el modelo. Necesitas al menos 25 muestras. Agrega más datos con /adddata e intenta nuevamente.")
    else:
        await update.message.reply_text("Modelo reentrenado exitosamente.")

# Función para eliminar códigos expirados periódicamente
def delete_expired_codes():
    utc_time_now = datetime.now(pytz.utc)
    temp_codes_collection.delete_many({"expiration": {"$lt": utc_time_now}})
    print("Códigos expirados eliminados.")

    # Programar la próxima ejecución (por ejemplo, cada hora)
    threading.Timer(3600, delete_expired_codes).start()

# Comando para generar el código temporal
async def getcode(update: Update, _: CallbackContext) -> None:
    user_id = update.effective_user.id
    args = update.message.text.split()
    
    if user_id == BOT_OWNER_ID:
        if len(args) > 1:
            try:
                expiration_duration = parse_time(args[1])
                expiration = datetime.now(pytz.utc) + expiration_duration  # Usar UTC para la expiración
                print(f"Duración de expiración: {expiration_duration}")
                print(f"Fecha y hora de expiración (UTC): {expiration}")
            except (ValueError, IndexError):
                await update.message.reply_text("Formato de tiempo no válido. Usa 'm' para minutos, 'h' para horas, o 'd' para días. Ejemplo: /getcode 2h")
                return
        else:
            expiration_duration = timedelta(hours=1)  # Valor por defecto: 1 hora
            expiration = datetime.now(pytz.utc) + expiration_duration
            print(f"Usando la duración por defecto: {expiration_duration}")

        code = generate_temp_code()
        temp_codes_collection.insert_one({"code": code, "user_id": None, "expiration": expiration})
        await update.message.reply_text(f"Código temporal generado: {code}. Expira en {expiration_duration}.")
    else:
        await update.message.reply_text("Solo el dueño del bot puede generar códigos temporales.")

# Comando para canjear el código
async def redeemcode(update: Update, _: CallbackContext) -> None:
    user_id = update.effective_user.id
    code = update.message.text.split()[1]

    utc_time_now = datetime.now(pytz.utc)  # Usar UTC para la comparación
    result = temp_codes_collection.find_one_and_update(
        {"code": code, "user_id": None, "expiration": {"$gt": utc_time_now}},
        {"$set": {"user_id": user_id}},
        return_document=True
    )

    if result:
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"has_access": True}},
            upsert=True
        )
        await update.message.reply_text("¡Código canjeado con éxito! Ahora puedes usar todos los comandos.")
    else:
        await update.message.reply_text("Código inválido o expirado.")

# Comando para banear un usuario
async def ban(update: Update, context: CallbackContext) -> None:
    try:
        user_id = update.effective_user.id
        if not has_permission(user_id): 
            await update.message.reply_text("Solo los administradores pueden usar este comando.")
            return

        target_user_id = int(context.args[0]) 

        result = users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"has_access": False}}
        )
        if result.modified_count > 0:
            await update.message.reply_text(f"""- [ User Banned Successfully! ]
<b>- - - - - - - - - - - - - - - - - - - - -</b>
<b>UserId: </b> {target_user_id}
<b>Status: </b> 200 - User Successfully Banned
<b>- - - - - - - - - - - - - - - - - - - - -</b>
<b>Bot By: </b> {Envs.Owner}""") 
        else:
            await update.message.reply_text(f"""- [ User Already Banned! ]
<b>- - - - - - - - - - - - - - - - - - - - -</b>
<b>UserId: </b> {target_user_id}
<b>Status: </b> 302 - Already Banned
<b>- - - - - - - - - - - - - - - - - - - - -</b>
<b>Bot By: </b> {Envs.Owner}""")

    except (IndexError, ValueError):
        await update.message.reply_text("Por favor, proporciona el ID del usuario al que deseas revocar el acceso. Ejemplo: /ban 123456789")
    except Exception as e:
        print(f"Error in Ban: [{e}]")
