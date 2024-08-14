from bot.bot_setup import app
from bot.command_handlers import delete_expired_codes

if __name__ == '__main__':
    try:
        delete_expired_codes()
        app.run_polling()
    except Exception as e:
        print(f"Error al ejecutar el bot: {e}")