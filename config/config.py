import urllib.parse
# import os

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


class Envs:
	appId = 2042114353 #Debe ir en formato int 
	apiHash = "c4a260814023dbf32e5f3adaf2799288"
	username = urllib.parse.quote_plus("jackdev")
	password = urllib.parse.quote_plus("@Y1i19860207J@[K")
	MongoUrl = f"mongodb+srv://{username}:{password}@bot0.qdusz.mongodb.net/"
	prefix = ['.','/','!', "$", "#", "<", ">", "(", ")"]
	Owner = "@jack_dev02"

	#Bot-Settings
	botToken = "6148092069:AAFEqKJC83lCmruZKTqivkPNVGura4cSsLQ" 
	botName = 'Ayli'
	botUsername = "@Aylidevbot"
	botChannel = "AyliChannel"

BOT_OWNER_ID = Envs.appId
