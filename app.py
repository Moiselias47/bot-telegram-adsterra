import os
import requests
from flask import Flask, request

# --- CONFIGURACIÓN PRINCIPAL ---
TOKEN = '8919461553:AAH6AsjYPKYPR9PcPCsO0AS0hjDVTGNiApg'

# El bot lee estas variables desde Render (Environment Variables)
RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://bot-telegram-adsterra.onrender.com')

# Volvemos a tu método original: leerá el link desde Render. 
# Dejé tu link actual escrito aquí solo como un respaldo de seguridad por si Render falla al leerlo.
ADSTERRA_LINK = os.environ.get('ADSTERRA_LINK', 'https://www.effectivecpmnetwork.com/gp8zzywpba?key=384a4119270137f0e9c42fe98024961f')

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Servidor Multi-Grupo Activo y Funcionando 🚀"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        
        # Procesar solicitudes de unión de CUALQUIER grupo
        if 'chat_join_request' in data:
            req = data['chat_join_request']
            user_id = req['from']['id']
            chat_id = req['chat']['id'] # ¡Atrapa el ID del grupo dinámicamente!
            user_name = req['from'].get('first_name', 'Usuario')
            
            # Construimos el link de destino escondiendo el ID del usuario y el del grupo
            link_destino = f"{RENDER_URL}/verificar?user_id={user_id}&chat_id={chat_id}"
            
            # Mensaje que el bot le envía al usuario en privado
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

    except Exception as e:
        print(f"Error procesando webhook: {e}")
    
    return "OK", 200

@app.route('/verificar', methods=['GET'])
def verificar():
    user_id = request.args.get('user_id')
    chat_id = request.args.get('chat_id')
    
    # Aseguramos leer el link más actualizado que hayas puesto en Render
    link_actual = os.environ.get('ADSTERRA_LINK', ADSTERRA_LINK)
    
    # Maneja si el link de Adsterra ya tiene un signo de interrogación o no
    separador = '&' if '?' in link_actual else '?'
    
    # Redirige al usuario a Adsterra, llevándose los IDs ocultos en la URL
    return f'<html><body><script>window.location.href = "{link_actual}{separador}user_id={user_id}&chat_id={chat_id}";</script></body></html>'

@app.route('/aprobar', methods=['GET'])
def aprobar():
    user_id = request.args.get('user_id')
    chat_id = request.args.get('chat_id')
    
    if not user_id or not chat_id:
        return "Faltan datos para la aprobación.", 400

    try:
        # El bot usa el chat_id exacto que viajó durante todo el proceso para abrir la puerta correcta
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
    

    

