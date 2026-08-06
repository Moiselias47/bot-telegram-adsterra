import os
from flask import Flask, request, render_template_string
import telebot

# --- CONFIGURACIÓN ---
# Render nos dará la URL automática más adelante
TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- RUTA 1: Para cuando el usuario pide unirse en Telegram ---
@bot.chat_join_request_handler()
def enviar_link_verificacion(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # URL de tu web que estará montada en Render
    render_url = os.environ.get('RENDER_EXTERNAL_URL', '')
    link_web = f"{render_url}/verificar?user_id={user_id}"
    
    texto = (
        f"¡Hola {user_name}! 🚀 Para confirmar tu acceso al grupo, "
        f"por favor entra al siguiente enlace y completa la verificación:\n\n{link_web}"
    )
    
    try:
        bot.send_message(user_id, texto)
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

# --- RUTA 2: El Webhook de Telegram ---
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# --- RUTA 3: La Página Web con el Botón y Adsterra ---
@app.route('/verificar')
def pagina_verificacion():
    user_id = request.args.get('user_id')
    # AQUÍ PEGARÁS TU SMART LINK DE ADSTERRA MAS ADELANTE
    adsterra_link = os.environ.get('ADSTERRA_LINK', 'https://www.google.com')
    
    html = f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verificación de Acceso</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; background: #0f172a; color: white; padding: 40px 20px; }}
            .card {{ background: #1e293b; padding: 30px; border-radius: 16px; max-width: 400px; margin: auto; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
            .btn {{ background: #22c55e; color: white; border: none; padding: 16px 28px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 20px; }}
            .btn:disabled {{ background: #64748b; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Acceso al Grupo</h2>
            <p>Haz clic en el botón de abajo para verificar tu cuenta e ingresar automáticamente.</p>
            <button id="btn" class="btn" onclick="aprobarAcceso()">VERIFICAR Y ENTRAR</button>
            <p id="msg" style="margin-top:15px; color:#38bdf8;"></p>
        </div>

        <script>
            function aprobarAcceso() {{
                // 1. Abrir el Smart Link de Adsterra en una pestaña secundaria
                window.open('{adsterra_link}', '_blank');
                
                // 2. Cambiar estado del botón
                let btn = document.getElementById('btn');
                let msg = document.getElementById('msg');
                btn.disabled = true;
                btn.innerText = "Procesando acceso...";
                msg.innerText = "Comprobando verificación... Revisa tu Telegram.";
                
                // 3. Avisar al servidor que apruebe al usuario en Telegram
                fetch('/aprobar?user_id={user_id}')
                    .then(r => r.text())
                    .then(data => {{
                        msg.innerText = "¡Listo! Ya fuiste aprobado. Entra a Telegram.";
                    }});
            }}
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

# --- RUTA 4: Ordenar a Telegram que apruebe al usuario ---
@app.route('/aprobar')
def aprobar_usuario():
    user_id = request.args.get('user_id')
    if user_id and CHAT_ID:
        try:
            bot.approve_chat_join_request(CHAT_ID, user_id)
            return "OK", 200
        except Exception as e:
            return f"Error: {e}", 400
    return "Missing parameters", 400

@app.route('/')
def home():
    return "Servidor del Bot Activo", 200
