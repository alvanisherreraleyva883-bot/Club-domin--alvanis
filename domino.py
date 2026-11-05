import os
import time
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "TU_BOT_TOKEN_AQUI")
GROUP_ID = -1004353226044
MIN_FICHAS = 5
PRECIO_POR_FICHA = 1
COMISION_CASA = 0.03
GANANCIA_CASA = 0
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

USERS = {}
MESAS = [
    {"id": 1, "apuesta": 5, "jugadores": []},
    {"id": 2, "apuesta": 5, "jugadores": []},
    {"id": 3, "apuesta": 10, "jugadores": []},
    {"id": 4, "apuesta": 10, "jugadores": []},
    {"id": 5, "apuesta": 20, "jugadores": []},
    {"id": 6, "apuesta": 20, "jugadores": []},
    {"id": 7, "apuesta": 50, "jugadores": []},
    {"id": 8, "apuesta": 50, "jugadores": []},
    {"id": 9, "apuesta": 100, "jugadores": []},
    {"id": 10, "apuesta": 100, "jugadores": []},
    {"id": 11, "apuesta": 200, "jugadores": []},
    {"id": 12, "apuesta": 200, "jugadores": []},
    {"id": 13, "apuesta": 500, "jugadores": []},
    {"id": 14, "apuesta": 500, "jugadores": []},
    {"id": 15, "apuesta": 1000, "jugadores": []},
    {"id": 16, "apuesta": 1000, "jugadores": []},
]
PEDIDOS = {}

HTML = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Cubadomino</title><style>*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif}body{background:#0a3d24;color:#fff;padding-bottom:70px}.top{background:#06301d;padding:12px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:10}.user-box{background:#000;border:1px solid #f5c518;border-radius:10px;padding:8px 12px;text-align:center;min-width:140px}.user-box b{font-size:20px;color:#f5c518;display:block}.btn-green{background:#22c55e;color:#fff;border:none;padding:10px 16px;border-radius:10px;font-weight:900;cursor:pointer}.hero{padding:14px}.hero h1{color:#f5c518;font-size:22px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px}.card{background:#0e4a2b;border:1px solid #1a6b3d;border-radius:16px;padding:12px;text-align:center}.card h3{color:#f5c518;margin-bottom:8px}.hidden{display:none!important}.modal{position:fixed;inset:0;background:rgba(0,0,0,.8);display:flex;align-items:flex-end;justify-content:center;z-index:50}.modal-box{background:#fff;color:#111;width:100%;max-width:480px;border-radius:20px 20px 0 0;padding:18px;padding-bottom:80px;max-height:90vh;overflow:auto}.modal-box input{width:100%;padding:13px;border:1px solid #ddd;border-radius:10px;margin:10px 0;font-size:16px}.big-btn{width:100%;background:#22c55e;color:#fff;border:none;padding:15px;border-radius:12px;font-weight:900;font-size:16px;cursor:pointer;margin-top:8px}.close{float:right;font-size:22px;cursor:pointer}.fichas-line{background:#f0fdf4;border:1px solid #bbf7d0;padding:10px;border-radius:10px;text-align:center;font-weight:800;color:#111}.mesa-wrap{padding:12px}.table{position:relative;background:radial-gradient(circle at 50% 30%,#1a8a4d,#0a4a28 70%);border:14px solid #5a2d0c;border-radius:28px;box-shadow:inset 0 0 0 4px #8b4513,inset 0 0 40px rgba(0,0,0,.6),0 10px 25px rgba(0,0,0,.5);aspect-ratio:9/11;display:flex;align-items:center;justify-content:center;overflow:hidden}.table:before{content:"CUBADOMINO";position:absolute;font-size:42px;font-weight:900;color:rgba(255,255,255,.07);transform:rotate(-20deg);letter-spacing:4px}.fichas-centro{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;max-width:220px;z-index:2}.ficha-domino{background:#fffdf5;width:38px;height:76px;border-radius:8px;border:2px solid #222;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;box-shadow:0 4px 8px rgba(0,0,0,.4);transform:rotate(-8deg)}.ficha-domino b{font-size:18px;color:#111}.ficha-domino span{width:28px;height:1px;background:#999;display:block}.seat{position:absolute;background:#111;border:2px solid #f5c518;border-radius:50px;padding:8px 12px;text-align:center;min-width:92px;font-size:12px;box-shadow:0 4px 10px rgba(0,0,0,.5);z-index:3}.seat.top{top:12px;left:50%;transform:translateX(-50%)}.seat.right{right:8px;top:50%;transform:translateY(-50%)}.seat.bottom{bottom:12px;left:50%;transform:translateX(-50%)}.seat.left{left:8px;top:50%;transform:translateY(-50%)}.bottom{position:fixed;bottom:0;left:0;right:0;background:#000;display:flex;justify-content:space-around;padding:12px;font-size:13px}.bottom b{color:#f5c518}.chip{width:44px;height:44px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ff4d5a,#c21624 60%,#8f0f1c);border:4px dashed #fff;box-shadow:0 0 0 3px #c21624,0 4px 8px rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;flex-shrink:0}.chip span{background:#fff;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:18px;color:#c21624;font-family:Arial}.chip-mini{width:32px;height:32px;border-width:3px}.chip-mini span{width:18px;height:18px;font-size:13px}.fichas-box{display:flex;align-items:center;gap:8px}</style></head><body><div class="top"><div><b>Cubadomino</b><div style="font-size:11px;opacity:.7">LOBBY - MESAS DISPONIBLES</div></div><div style="display:flex;gap:8px;align-items:center"><div class="user-box"><span id="nombreUser">...</span><div class="fichas-box" style="justify-content:center"><div class="chip"><span>D</span></div><div><b id="fichasUser">0</b><span>FICHAS</span></div></div></div><button class="btn-green" onclick="abrirRecarga()">+ RECARGAR</button></div></div><div class="hero"><h1>CLUB DE DOMINÓ CUBANO</h1><p>Elige tu mesa y siéntate a jugar<br><small>Comisión de la casa: 3% en cada partida</small></p></div><div id="lobby" class="grid"></div><div id="mesaView" class="mesa-wrap hidden"><button onclick="volver()" style="background:#fff;border:none;padding:8px 14px;border-radius:20px;font-weight:800;margin-bottom:10px;cursor:pointer">← Volver</button><div style="display:flex;justify-content:space-between;margin-bottom:8px"><b id="tituloMesa">Mesa de 5 fichas</b><span id="jugadoresMesa">0 de 4</span></div><div class="table"><div class="fichas-centro"><div class="ficha-domino"><b>6</b><span></span><b>6</b></div><div class="ficha-domino" style="transform:rotate(12deg)"><b>5</b><span></span><b>3</b></div><div class="ficha-domino" style="transform:rotate(-3deg)"><b>4</b><span></span><b>1</b></div><div class="ficha-domino" style="transform:rotate(8deg)"><b>2</b><span></span><b>2</b></div></div><div class="seat top"><b id="pTop">Esperando...</b></div><div class="seat right"><b id="pRight">Esperando...</b></div><div class="seat bottom"><b id="pYou">Tú</b></div><div class="seat left"><b>Vacío</b><br><button onclick="sentarse()" style="background:#f5c518;border:none;padding:6px 10px;border-radius:8px;font-weight:900">Sentarse</button></div></div><button class="big-btn" onclick="jugarMano()">JUGAR MANO</button><p style="text-align:center;margin-top:8px" id="estadoMesa">Esperando jugadores...</p></div><div id="modalRecarga" class="modal hidden"><div class="modal-box"><span class="close" onclick="cerrarTodo()">×</span><h2>Recargar Fichas</h2><p><b>1 ficha = 1 CUP</b></p><div style="background:#fef9c3;border:2px solid #facc15;padding:12px;border-radius:12px;margin:10px 0;text-align:center"><div style="font-size:13px">💳 TRANSFIERE AQUÍ ANTES DE ENVIAR:</div><div style="font-size:18px;font-weight:900;margin:6px 0">Tarjeta CUP: 9238-1299-7507-3018</div><div style="font-size:18px;font-weight:900">Móvil a confirmar: 55348244</div><div style="font-size:12px;margin-top:6px">Después de transferir, sube la captura abajo 👇</div></div><div class="fichas-line">Fichas: <span id="fichasModal">0</span></div><input type="number" id="cantRecarga" min="5" value="5"><div>Total: <span id="totalPagar">5 CUP</span></div><input id="movilRecarga" placeholder="Tu móvil 5XXXXXXX"><input type="file" id="captura" accept="image/*"><button class="big-btn" onclick="enviarRecarga()">ENVIAR</button><p style="font-size:12px;margin-top:8px">Cuando el admin pulse ✅ CONFIRMAR, se te acreditan solas.</p></div></div><div id="modalRetiro" class="modal hidden"><div class="modal-box"><span class="close" onclick="cerrarTodo()">×</span><h2>Retirar Fichas</h2><p><b>1 ficha = 1 CUP</b></p><div class="fichas-line">Fichas: <span id="fichasRetiro">0</span></div><input type="number" id="cantRetiro" min="5" value="5"><input id="tarjetaRetiro" placeholder="Tarjeta CUP"><input id="movilRetiro" placeholder="Móvil"><button class="big-btn" style="background:#f59e0b" onclick="enviarRetiro()">SOLICITAR RETIRO</button></div></div><div class="bottom"><span>🏠 <b>Lobby</b></span><span onclick="abrirRecarga()">🛒 Recargar</span><span onclick="abrirRetiro()">💸 Retirar</span><span onclick="cambiarNombre()">👤 Perfil</span></div><script>let userId=localStorage.getItem('cuba_user_id');if(!userId){userId='u_'+Date.now();localStorage.setItem('cuba_user_id',userId);}let userNombre=localStorage.getItem('cuba_nombre');if(!userNombre){userNombre=prompt("¿Cómo te llamas?");if(!userNombre)userNombre="Jugador";localStorage.setItem('cuba_nombre',userNombre);}let user={id:userId,nombre:userNombre,fichas:0};let mesas=[];let mesaActual=null;async function sync(){try{let r=await fetch('/api/me',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:user.id,nombre:user.nombre})});let d=await r.json();user=d.user;let r2=await fetch('/api/mesas');mesas=await r2.json();render();}catch(e){}}function render(){document.getElementById('nombreUser').textContent=user.nombre;document.getElementById('fichasUser').textContent=user.fichas;document.getElementById('fichasModal').textContent=user.fichas;document.getElementById('fichasRetiro').textContent=user.fichas;let html='';mesas.forEach(m=>{html+=`<div class="card"><h3>MESA DE ${m.apuesta} FICHAS</h3><div><b>${m.jugadores.length} de 4</b> • Apuesta: ${m.apuesta} fichas</div><button class="btn-green" style="width:100%;margin-top:8px" onclick="entrarMesa(${m.id})">ENTRAR</button></div>`;});document.getElementById('lobby').innerHTML=html;if(mesaActual){let m=mesas.find(x=>x.id===mesaActual);if(m){document.getElementById('tituloMesa').textContent=`Mesa de ${m.apuesta} fichas`;document.getElementById('jugadoresMesa').textContent=`${m.jugadores.length} de 4`;document.getElementById('pTop').textContent=m.jugadores[1]?.nombre||'Esperando...';document.getElementById('pRight').textContent=m.jugadores[2]?.nombre||'Esperando...';document.getElementById('pYou').textContent=m.jugadores[0]?.nombre||'Tú';}}}function entrarMesa(id){mesaActual=id;document.getElementById('lobby').classList.add('hidden');document.getElementById('mesaView').classList.remove('hidden');sync();}function volver(){document.getElementById('mesaView').classList.add('hidden');document.getElementById('lobby').classList.remove('hidden');}async function sentarse(){let m=mesas.find(x=>x.id===mesaActual);if(user.fichas<m.apuesta){alert('No tienes fichas. Recarga mínimo 5.');abrirRecarga();return;}let r=await fetch('/api/sentarse',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,mesa_id:mesaActual})});let d=await r.json();if(!d.ok)alert(d.error);else sync();}async function jugarMano(){if(!mesaActual)return alert('Entra a una mesa primero');let r=await fetch('/api/ganar_mano',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,mesa_id:mesaActual})});let d=await r.json();if(!d.ok)return alert(d.error);alert('¡Ganaste! Bote: '+d.bote+' | Comisión casa 3%: '+d.comision+' | Te llevas: '+d.ganancia);sync();}function abrirRecarga(){document.getElementById('modalRecarga').classList.remove('hidden');}function abrirRetiro(){document.getElementById('modalRetiro').classList.remove('hidden');}function cerrarTodo(){document.querySelectorAll('.modal').forEach(e=>e.classList.add('hidden'));}function cambiarNombre(){let n=prompt("Tu nombre:",user.nombre);if(n){user.nombre=n;localStorage.setItem('cuba_nombre',n);sync();}}document.getElementById('cantRecarga').addEventListener('input',e=>{document.getElementById('totalPagar').textContent=(parseInt(e.target.value)||0)+' CUP';});async function enviarRecarga(){let cant=parseInt(document.getElementById('cantRecarga').value);if(!cant||cant<5)return alert('Mínimo 5');let movil=document.getElementById('movilRecarga').value;if(!movil)return alert('Pon tu móvil');let file=document.getElementById('captura').files[0];let fd=new FormData();fd.append('user_id',user.id);fd.append('cantidad',cant);fd.append('movil',movil);if(file)fd.append('captura',file);let r=await fetch('/api/recarga',{method:'POST',body:fd});let d=await r.json();if(d.ok){alert('Enviado. Cuando el admin pulse CONFIRMAR, se te acreditan solas.');cerrarTodo();}else alert(d.error);}async function enviarRetiro(){let cant=parseInt(document.getElementById('cantRetiro').value);if(!cant||cant<5)return alert('Mínimo 5');if(cant>user.fichas)return alert('No tienes tantas');let tarjeta=document.getElementById('tarjetaRetiro').value,movil=document.getElementById('movilRetiro').value;if(!tarjeta||!movil)return alert('Pon tarjeta y móvil');let r=await fetch('/api/retiro',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,cantidad:cant,tarjeta,movil})});let d=await r.json();if(d.ok){alert('Enviado a Telegram.');cerrarTodo();}else alert(d.error);}sync();setInterval(sync,3000);</script></body></html>"""

def enviar_telegram(texto, pedido_id, es_retiro=False):
    if BOT_TOKEN == "TU_BOT_TOKEN_AQUI":
        return False
    boton = "✅ CONFIRMAR RETIRO" if es_retiro else "✅ CONFIRMAR"
    payload = {"chat_id": GROUP_ID, "text": texto, "reply_markup": {"inline_keyboard": [[{"text": boton, "callback_data": f"confirmar_{pedido_id}"}]]}}
    try:
        r = requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=10)
        return r.ok
    except Exception as e:
        print("Error Telegram:", e)
        return False

def enviar_foto_telegram(photo_path, caption, pedido_id, es_retiro=False):
    if BOT_TOKEN == "TU_BOT_TOKEN_AQUI":
        return False
    boton = "✅ CONFIRMAR RETIRO" if es_retiro else "✅ CONFIRMAR"
    try:
        with open(photo_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": GROUP_ID, "caption": caption, "reply_markup": json.dumps({"inline_keyboard": [[{"text": boton, "callback_data": f"confirmar_{pedido_id}"}]]})}
            r = requests.post(f"{TELEGRAM_API}/sendPhoto", data=data, files=files, timeout=20)
            return r.ok
    except Exception as e:
        print("Error foto:", e)
        return False

@app.route("/")
def index():
    return HTML

@app.route("/<path:path>")
def catch_all(path):
    return HTML

@app.route("/api/me", methods=["POST"])
def api_me():
    data = request.get_json(force=True)
    uid = data.get("id")
    nombre = data.get("nombre", "Jugador")
    if uid not in USERS:
        USERS[uid] = {"id": uid, "nombre": nombre, "fichas": 0}
    else:
        USERS[uid]["nombre"] = nombre
    return jsonify({"user": USERS[uid]})

@app.route("/api/ganar_mano", methods=["POST"])
def api_ganar_mano():
    global GANANCIA_CASA
    data = request.get_json(force=True)
    uid = data.get("user_id")
    mesa_id = data.get("mesa_id")
    user = USERS.get(uid)
    mesa = next((m for m in MESAS if m["id"] == mesa_id), None)
    if not user or not mesa:
        return jsonify({"ok": False, "error": "No encontrado"}), 400
    bote = mesa["apuesta"] * len(mesa["jugadores"])
    if bote <= 0:
        return jsonify({"ok": False, "error": "Sin jugadores"}), 400
    comision = int(bote * COMISION_CASA)
    ganancia = bote - comision
    GANANCIA_CASA += comision
    user["fichas"] += ganancia
    mesa["jugadores"] = []
    return jsonify({"ok": True, "bote": bote, "ganancia": ganancia, "comision": comision, "casa_total": GANANCIA_CASA, "fichas": user["fichas"]})

@app.route("/api/mesas")
def api_mesas():
    return jsonify(MESAS)

@app.route("/api/sentarse", methods=["POST"])
def api_sentarse():
    data = request.get_json(force=True)
    uid = data.get("user_id")
    mesa_id = data.get("mesa_id")
    user = USERS.get(uid)
    if not user:
        return jsonify({"ok": False, "error": "Usuario no encontrado"}), 400
    mesa = next((m for m in MESAS if m["id"] == mesa_id), None)
    if not mesa:
        return jsonify({"ok": False, "error": "Mesa no existe"}), 400
    if any(j["id"] == uid for j in mesa["jugadores"]):
        return jsonify({"ok": False, "error": "Ya estás sentado"})
    if len(mesa["jugadores"]) >= 4:
        return jsonify({"ok": False, "error": "Mesa llena"})
    if user["fichas"] < mesa["apuesta"]:
        return jsonify({"ok": False, "error": "No tienes fichas suficientes. Recarga mínimo 5."})
    mesa["jugadores"].append({"id": uid, "nombre": user["nombre"]})
    return jsonify({"ok": True, "mesa": mesa})

@app.route("/api/recarga", methods=["POST"])
def api_recarga():
    uid = request.form.get("user_id")
    cantidad = int(request.form.get("cantidad", 0))
    movil = request.form.get("movil", "")
    user = USERS.get(uid)
    if not user:
        return jsonify({"ok": False, "error": "Usuario no encontrado"}), 400
    if cantidad < MIN_FICHAS:
        return jsonify({"ok": False, "error": f"Mínimo {MIN_FICHAS} fichas"}), 400
    pedido_id = f"REC-{int(time.time()*1000)}"
    PEDIDOS[pedido_id] = {"tipo": "recarga", "user_id": uid, "cantidad": cantidad, "movil": movil, "estado": "pendiente"}
    total = cantidad * PRECIO_POR_FICHA
    texto = f"🧾 NUEVA RECARGA\n👤 Usuario: {user['nombre']}\n🆔 ID: {uid}\n💰 Fichas: {cantidad}\n💵 Total: {total} CUP\n📱 Móvil: {movil}\nPedido: {pedido_id}\n\n1 ficha = 1 CUP"
    foto = request.files.get("captura")
    if foto and foto.filename:
        path = f"/tmp/{pedido_id}.jpg"
        foto.save(path)
        enviado = enviar_foto_telegram(path, texto, pedido_id, es_retiro=False)
        if not enviado:
            enviar_telegram(texto, pedido_id)
    else:
        enviar_telegram(texto, pedido_id)
    return jsonify({"ok": True, "pedido": pedido_id})

@app.route("/api/retiro", methods=["POST"])
def api_retiro():
    data = request.get_json(force=True)
    uid = data.get("user_id")
    cantidad = int(data.get("cantidad", 0))
    tarjeta = data.get("tarjeta", "")
    movil = data.get("movil", "")
    user = USERS.get(uid)
    if not user:
        return jsonify({"ok": False, "error": "Usuario no encontrado"}), 400
    if cantidad < MIN_FICHAS:
        return jsonify({"ok": False, "error": f"Mínimo {MIN_FICHAS} fichas"}), 400
    if cantidad > user["fichas"]:
        return jsonify({"ok": False, "error": "No tienes tantas fichas"}), 400
    pedido_id = f"RET-{int(time.time()*1000)}"
    PEDIDOS[pedido_id] = {"tipo": "retiro", "user_id": uid, "cantidad": cantidad, "tarjeta": tarjeta, "movil": movil, "estado": "pendiente"}
    texto = f"💸 NUEVO RETIRO\n👤 Usuario: {user['nombre']}\n🆔 ID: {uid}\n💰 Fichas: {cantidad}\n💵 Total: {cantidad * PRECIO_POR_FICHA} CUP\n💳 Tarjeta: {tarjeta}\n📱 Móvil: {movil}\nPedido: {pedido_id}\n\n1 ficha = 1 CUP"
    enviar_telegram(texto, pedido_id, es_retiro=True)
    return jsonify({"ok": True, "pedido": pedido_id})

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    if "callback_query" in update:
        cb = update["callback_query"]
        data = cb.get("data", "")
        chat_id = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]
        if data.startswith("confirmar_"):
            pedido_id = data.replace("confirmar_", "")
            pedido = PEDIDOS.get(pedido_id)
            if not pedido:
                answer_callback(cb["id"], "Pedido no encontrado")
                return jsonify({"ok": True})
            if pedido["estado"] != "pendiente":
                answer_callback(cb["id"], "Ya fue confirmado")
                return jsonify({"ok": True})
            user = USERS.get(pedido["user_id"])
            if not user:
                answer_callback(cb["id"], "Usuario no encontrado")
                return jsonify({"ok": True})
            if pedido["tipo"] == "recarga":
                user["fichas"] += pedido["cantidad"]
                msg = f"✅ CONFIRMADO\nSe acreditaron {pedido['cantidad']} fichas a {user['nombre']}\nFichas ahora: {user['fichas']}"
            else:
                if user["fichas"] < pedido["cantidad"]:
                    answer_callback(cb["id"], "El usuario ya no tiene esas fichas")
                    return jsonify({"ok": True})
                user["fichas"] -= pedido["cantidad"]
                msg = f"✅ RETIRO CONFIRMADO\nSe descontaron {pedido['cantidad']} fichas a {user['nombre']}\nFichas ahora: {user['fichas']}"
            pedido["estado"] = "confirmado"
            answer_callback(cb["id"], "Confirmado ✅")
            try:
                if "photo" in cb["message"]:
                    old = cb["message"].get("caption", "")
                    requests.post(f"{TELEGRAM_API}/editMessageCaption", json={"chat_id": chat_id, "message_id": message_id, "caption": old + f"\n\n{msg}"}, timeout=10)
                else:
                    old = cb["message"].get("text", "")
                    requests.post(f"{TELEGRAM_API}/editMessageText", json={"chat_id": chat_id, "message_id": message_id, "text": old + f"\n\n{msg}"}, timeout=10)
            except Exception as e:
                print(e)
            return jsonify({"ok": True})
    return jsonify({"ok": True})

def answer_callback(callback_id, text):
    try:
        requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json={"callback_query_id": callback_id, "text": text}, timeout=10)
    except Exception as e:
        print(e)

@app.route("/api/confirmar/<pedido_id>")
def confirmar_manual(pedido_id):
    pedido = PEDIDOS.get(pedido_id)
    if not pedido or pedido["estado"] != "pendiente":
        return jsonify({"ok": False, "error": "Pedido no valido"})
    user = USERS.get(pedido["user_id"])
    if pedido["tipo"] == "recarga":
        user["fichas"] += pedido["cantidad"]
    else:
        user["fichas"] -= pedido["cantidad"]
    pedido["estado"] = "confirmado"
    return jsonify({"ok": True, "user": user})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
