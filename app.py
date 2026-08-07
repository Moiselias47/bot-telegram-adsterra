import os
import requests
from flask import Flask, request

# --- CONFIGURACIÓN ---
TOKEN = '8919461553:AAH6AsjYPKYPR9PcPCsO0AS0hjDVTGNiApg'
CHAT_ID = '-1004335462680'
RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://bot-telegram-adsterra.onrender.com')

app = Flask(__name__)

# --- RUTA PRINCIPAL ---
@app.route('/', methods=['GET'])
def home():
    return "Servidor del Bot Activo"

# --- RUTA WEBHOOK DIRECTA ---
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        print("DATOS RECIBIDOS DE TELEGRAM:", data)
        
        # 1. Si el usuario envía un mensaje directo (ej. /start)
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            if text.startswith('/start'):
                user_id = message['from']['id']
                link_destino = f"{RENDER_URL}/verificar?user_id={user_id}"
                
                payload = {
                    'chat_id': chat_id,
                    'text': "¡Hola! Usa este botón para probar la verificación:",
                    'reply_markup': {
                        'inline_keyboard': [[
                            {'text': "Verificar ahora", 'url': link_destino}
                        ]]
                    }
                }
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)

        # 2. Si el usuario solicita unirse al grupo
        elif 'chat_join_request' in data:
            req = data['chat_join_request']
            user_id = req['from']['id']
            user_name = req['from'].get('first_name', 'Usuario')
            link_destino = f"{RENDER_URL}/verificar?user_id={user_id}"
            
            payload = {
                'chat_id': user_id,
                'text': f"¡Hola {user_name}! Para unirte al grupo, completa la verificación aquí:",
                'reply_markup': {
                    'inline_keyboard': [[
                        {'text': "Verificar para entrar", 'url': link_destino}
                    ]]
                }
            }
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)

    except Exception as e:
        print(f"Error procesando webhook: {e}")
    
    return "OK", 200

# --- RUTA DE VERIFICACIÓN ---
@app.route('/verificar', methods=['GET'])
def verificar():
    user_id = request.args.get('user_id')
    adsterra_link = os.environ.get('ADSTERRA_LINK', 'https://tu-link-de-adsterra-aqui.com')
    return f'<html><body><script>window.location.href = "{adsterra_link}?user_id={user_id}";</script></body></html>'

# --- RUTA PARA APROBAR EL INGRESO ---
@app.route('/aprobar', methods=['GET'])
def aprobar():
    user_id = request.args.get('user_id')
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/approveChatJoinRequest"
        res = requests.post(url, json={'chat_id': CHAT_ID, 'user_id': int(user_id)})
        if res.json().get('ok'):
            return "¡Verificación exitosa! Ya puedes volver al grupo."
        else:
            return f"Error de Telegram: {res.json().get('description')}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))


    

