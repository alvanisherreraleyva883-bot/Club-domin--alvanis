import os
import time
import json
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BOT_TOKEN = os.environ.get("BOT_TOKEN", "TU_BOT_TOKEN_AQUI")
GROUP_ID = -1004353226044
MIN_FICHAS = 5
PRECIO_POR_FICHA = 1
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

USERS = {}
MESAS = [
    {"id": 1, "apuesta": 5, "jugadores": []},
    {"id": 2, "apuesta": 5, "jugadores": []},
    {"id": 3, "apuesta": 10, "jugadores": []},
    {"id": 4, "apuesta": 10, "jugadores": []},
    {"id": 5, "apuesta": 20, "jugadores": []},
    {"id": 6, "apuesta": 20, "jugadores": []},
]
PEDIDOS = {}

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
    return send_from_directory(BASE_DIR, "index.html")

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
                requests.post(f"{TELEGRAM_API}/editMessageText", json={"chat_id": chat_id, "message_id": message_id, "text": cb["message"].get("text", "") + f"\n\n{msg}"}, timeout=10)
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
