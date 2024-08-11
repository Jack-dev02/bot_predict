
from telegram.ext import ApplicationBuilder, CommandHandler
from bot.command_handlers import start, help, compare, adddata, deletedata, getcode, redeemcode, ban, train
from config.config import Envs

TOKEN = Envs.botToken
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("compare", compare))
app.add_handler(CommandHandler("adddata", adddata))
app.add_handler(CommandHandler("train", train))
app.add_handler(CommandHandler("deletedata", deletedata))
app.add_handler(CommandHandler("getcode", getcode))
app.add_handler(CommandHandler("redeemcode", redeemcode))
app.add_handler(CommandHandler("ban", ban))

if __name__ == '__main__':
    app.run_polling()
    