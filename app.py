import os
from flask import Flask, request, render_template, redirect
import telebot

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL')

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


# --- RUTA PRINCIPAL (Para verificar que el servidor está vivo) ---
@app.route('/', methods=['GET'])
def home():
    return "Servidor del Bot Activo"


# --- RUTA WEBHOOK DE TELEGRAM (Usa el Token automáticamente) ---
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    else:
        return "Invalid content type", 403


# --- CAPTURAR SOLICITUD DE UNIÓN AL GRUPO ---
@bot.chat_join_request_handler()
def enviar_link_verificacion(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Enlace que lleva al usuario a tu página web con el anuncio
    link_destino = f"{RENDER_URL}/verificar?user_id={user_id}"

    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(text="Verificar para entrar", url=link_destino)
    markup.add(btn)

    bot.send_message(
        chat_id=user_id,
        text=f"¡Hola {user_name}! Para unirte al grupo, por favor completa la verificación haciendo clic en el siguiente botón:",
        reply_markup=markup
    )


# --- RUTA DE VERIFICACIÓN WEB (Adsterra) ---
@app.route('/verificar', methods=['GET'])
def verificar():
    user_id = request.args.get('user_id')
    adsterra_link = os.environ.get('ADSTERRA_LINK')

    # Aquí puedes mostrar una página simple o redirigir al usuario al anuncio
    return render_template('verificar.html', adsterra_link=adsterra_link, user_id=user_id)


# --- RUTA PARA APROBAR AL USUARIO TRAS VERIFICAR ---
@app.route('/aprobar', methods=['GET'])
def aprobar():
    user_id = request.args.get('user_id')
    
    try:
        # Aprueba la entrada del usuario al grupo de Telegram automáticamente
        bot.approve_chat_join_request(chat_id=CHAT_ID, user_id=int(user_id))
        return "¡Verificación exitosa! Ya puedes volver al grupo de Telegram.", 200
    except Exception as e:
        return f"Hubo un error al aprobar tu acceso: {str(e)}", 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

