import urllib.parse
import os
from dotenv import load_dotenv

# class Envs:
#     appId = int(os.getenv("APP_ID")) 
#     apiHash = os.getenv("API_HASH")
#     username = urllib.parse.quote_plus(os.getenv("USERNAME"))
#     password = urllib.parse.quote_plus(os.getenv("PASSWORD"))
#     MongoUrl = f"mongodb+srv://{username}:{password}@bot0.qdusz.mongodb.net/"
#     Owner = os.getenv("OWNER")

#     #Bot-Settings
#     botToken = os.getenv("BOT_TOKEN") 
#     botName = os.getenv("BOT_NAME")
#     botUsername = os.getenv("BOT_USERNAME")
#     botChannel = os.getenv("BOT_CHANNEL")

# BOT_OWNER_ID = Envs.appId
load_dotenv()

class Envs:
	# appId = int("APP_ID") #Debe ir en formato int 
	appId = int(os.getenv.get("APP_ID")) 
	username = urllib.parse.quote_plus(os.getenv("USER_NAME"))
	password = urllib.parse.quote_plus(os.getenv("PASS_KEY"))
	MongoUrl = f"mongodb+srv://{username}:{password}@bot0.qdusz.mongodb.net/"
	Owner = "@jack_dev02"

	#Bot-Settings
	botToken = os.getenv("BOT_TOKEN") 

BOT_OWNER_ID = Envs.appId
