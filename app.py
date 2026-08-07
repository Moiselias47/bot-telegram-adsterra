import os
from flask import Flask, request, render_template
import telebot

# --- CONFIGURACIÓN ---
TOKEN = '8919461553:AAH6AsjYPKYPR9PcPCsO0AS0hjDVTGNiApg'
CHAT_ID = '-1004335462680'
# Asegúrate de que en Render, en la pestaña Environment, 
# la variable RENDER_EXTERNAL_URL esté configurada con la dirección de tu web.
RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://bot-telegram-adsterra.onrender.com')

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- RUTA PRINCIPAL ---
@app.route('/', methods=['GET'])
def home():
    return "Servidor del Bot Activo"

# --- RUTA WEBHOOK DE TELEGRAM ---
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

# --- CAPTURAR SOLICITUD DE UNIÓN ---
@bot.chat_join_request_handler()
def enviar_link_verificacion(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Enlace hacia tu web de verificación
    link_destino = f"{RENDER_URL}/verificar?user_id={user_id}"

    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(text="Verificar para entrar", url=link_destino)
    markup.add(btn)

    bot.send_message(
        chat_id=user_id,
        text=f"¡Hola {user_name}! Para unirte al grupo, completa la verificación aquí:",
        reply_markup=markup
    )

# --- PRUEBA DIRECTA (/start) ---
@bot.message_handler(commands=['start'])
def comando_start(message):
    user_id = message.from_user.id
    link_destino = f"{RENDER_URL}/verificar?user_id={user_id}"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text="Verificar ahora", url=link_destino))
    bot.send_message(message.chat.id, "¡Hola! Usa este botón para probar la verificación:", reply_markup=markup)

# --- RUTA DE VERIFICACIÓN ---
@app.route('/verificar', methods=['GET'])
def verificar():
    user_id = request.args.get('user_id')
    # Adsterra link guardado en variables de entorno de Render
    adsterra_link = os.environ.get('ADSTERRA_LINK', 'https://tu-link-de-adsterra-aqui.com')
    return f'<html><body><script>window.location.href = "{adsterra_link}?user_id={user_id}";</script></body></html>'

# --- RUTA PARA APROBAR ---
@app.route('/aprobar', methods=['GET'])
def aprobar():
    user_id = request.args.get('user_id')
    try:
        bot.approve_chat_join_request(chat_id=CHAT_ID, user_id=int(user_id))
        return "¡Verificación exitosa! Ya puedes volver al grupo."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


