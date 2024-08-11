import urllib.parse
import os

class Envs:
    appId = int(os.getenv("APP_ID")) 
    apiHash = os.getenv("API_HASH")
    username = urllib.parse.quote_plus(os.getenv("USERNAME"))
    password = urllib.parse.quote_plus(os.getenv("PASSWORD"))
    MongoUrl = f"mongodb+srv://{username}:{password}@bot0.qdusz.mongodb.net/"
    prefix = ['.','/','!', "$", "#", "<", ">", "(", ")"]
    Owner = os.getenv("OWNER")

    #Bot-Settings
    botToken = os.getenv("BOT_TOKEN") 
    botName = os.getenv("BOT_NAME")
    botUsername = os.getenv("BOT_USERNAME")
    botChannel = os.getenv("BOT_CHANNEL")

BOT_OWNER_ID = Envs.appId
