import os
import requests
from flask import Flask, request

# --- CONFIGURACIÓN PRINCIPAL ---
TOKEN = '8919461553:AAH6AsjYPKYPR9PcPCsO0AS0hjDVTGNiApg'

# El bot lee estas variables desde Render
RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://bot-telegram-adsterra.onrender.com')
ADSTERRA_LINK = os.environ.get('ADSTERRA_LINK', 'https://www.effectivecpmnetwork.com/gp8zzywpba?key=384a4119270137f0e9c42fe98024961f')

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Servidor Multi-Grupo Activo y Funcionando 🚀"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        
        # 1. FUNCIÓN DE ENTRADA: Procesar solicitudes de unión por privado
        if 'chat_join_request' in data:
            req = data['chat_join_request']
            user_id = req['from']['id']
            chat_id = req['chat']['id'] 
            user_name = req['from'].get('first_name', 'Usuario')
            
            link_destino = f"{RENDER_URL}/verificar?user_id={user_id}&chat_id={chat_id}"
            
            payload = {
                'chat_id': user_id,
                'text': f"¡Hola {user_name}! Para unirte al grupo, completa la verificación de seguridad haciendo clic aquí:",
                'reply_markup': {
                    'inline_keyboard': [[
                        {'text': "Verificar para entrar", 'url': link_destino}
                    ]]
                }
            }
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)

        # 2. FUNCIONES DENTRO DEL GRUPO
        elif 'message' in data:
            msg = data['message']
            chat_id = msg['chat']['id']
            
            link_actual = os.environ.get('ADSTERRA_LINK', ADSTERRA_LINK)

            # A. Cuando un usuario nuevo ENTRA al grupo
            if 'new_chat_members' in msg:
                for new_user in msg['new_chat_members']:
                    # Evitamos que el bot salude a otros bots o a sí mismo
                    if new_user.get('is_bot'):
                        continue
                        
                    nombre = new_user.get('first_name', 'Usuario')
                    payload = {
                        'chat_id': chat_id,
                        'text': f"¡Bienvenido/a al grupo, {nombre}! 🔥\n\nNo olvides revisar nuestro contenido exclusivo haciendo clic aquí abajo 👇",
                        'reply_markup': {
                            'inline_keyboard': [[
                                {'text': "👉 Ver Contenido 👈", 'url': link_actual}
                            ]]
                        }
                    }
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)

            # B. Comando manual /promo (Lo dejé por si algún día quieres forzar el mensaje)
            text = msg.get('text', '')
            if text == '/promo':
                payload = {
                    'chat_id': chat_id,
                    'text': "🔥 ¡Haz clic en el botón de abajo para ver el contenido completo y sin límites! 👇",
                    'reply_markup': {
                        'inline_keyboard': [[
                            {'text': "👉 Ver Contenido 👈", 'url': link_actual}
                        ]]
                    }
                }
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)

    except Exception as e:
        print(f"Error procesando webhook: {e}")
    
    return "OK", 200

@app.route('/verificar', methods=['GET'])
def verificar():
    user_id = request.args.get('user_id')
    chat_id = request.args.get('chat_id')
    
    link_actual = os.environ.get('ADSTERRA_LINK', ADSTERRA_LINK)
    separador = '&' if '?' in link_actual else '?'
    
    return f'<html><body><script>window.location.href = "{link_actual}{separador}user_id={user_id}&chat_id={chat_id}";</script></body></html>'

@app.route('/aprobar', methods=['GET'])
def aprobar():
    user_id = request.args.get('user_id')
    chat_id = request.args.get('chat_id')
    
    if not user_id or not chat_id:
        return "Faltan datos para la aprobación.", 400

    try:
        url = f"https://api.telegram.org/bot{TOKEN}/approveChatJoinRequest"
        res = requests.post(url, json={'chat_id': int(chat_id), 'user_id': int(user_id)})
        
        if res.json().get('ok'):
            return "¡Verificación exitosa! Ya has sido aprobado en el grupo. Puedes volver a Telegram."
        else:
            return f"Error de Telegram: {res.json().get('description')}"
    except Exception as e:
        return f"Error interno: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
    

