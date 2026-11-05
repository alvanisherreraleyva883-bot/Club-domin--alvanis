import os, json, time, random, threading
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
GROUP_ID = os.environ.get("GROUP_ID", "") or "-1004353226044"
ADMIN_ID = os.environ.get("ADMIN_ID", "")
BASE_URL = os.environ.get("BASE_URL", "https://club-domin--alvanis.onrender.com")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ============ DATOS ============
USUARIOS = {}
PEDIDOS = {}
MESAS = {}
PARTIDAS = {}

APUESTAS = [5,10,20,50,100,200,500,1000]
for apuesta in APUESTAS:
    for n in [1,2]:
        mid = f"mesa-{apuesta}-{n}"
        MESAS[mid] = {"id": mid, "apuesta": apuesta, "nombre": f"Mesa {apuesta} #{n}", "jugadores": [], "max": 4}

TARJETA = "9238-1299-7507-3018"
MOVIL_CONFIRMAR = "55348244"

def tg(method, data):
    try:
        r = requests.post(f"{TELEGRAM_API}/{method}", json=data, timeout=10).json()
        print("TG", method, r)
        return r
    except Exception as e:
        print("TG ERROR", e)
        return {}

def saldo(uid):
    return USUARIOS.get(str(uid), {}).get("saldo", 0)

def add_saldo(uid, monto):
    u = USUARIOS.setdefault(str(uid), {"nombre": "Jugador", "saldo": 0})
    u["saldo"] = u.get("saldo", 0) + monto
    return u["saldo"]

# ============ LOGICA DOMINO ============
def crear_fichas():
    fichas = []
    for i in range(7):
        for j in range(i, 7):
            fichas.append([i, j])
    random.shuffle(fichas)
    return fichas

def iniciar_partida(mesa_id):
    mesa = MESAS[mesa_id]
    jugadores = mesa["jugadores"][:]
    if len(jugadores) < 2:
        return None
    fichas = crear_fichas()
    manos = {}
    for uid in jugadores:
        manos[str(uid)] = [fichas.pop() for _ in range(7)]
    inicio = jugadores[0]
    for uid in jugadores:
        if [6,6] in manos[str(uid)]:
            inicio = uid
            break
    PARTIDAS[mesa_id] = {
        "jugadores": jugadores,
        "manos": manos,
        "mesa_fichas": [],
        "turno": inicio,
        "turno_inicio": time.time(),
        "extremo_izq": None,
        "extremo_der": None,
        "pasadas": 0,
        "terminada": False
    }
    return PARTIDAS[mesa_id]

def verificar_timeout(mesa_id):
    p = PARTIDAS.get(mesa_id)
    if not p or p["terminada"]:
        return p
    if time.time() - p["turno_inicio"] > 30:
        idx = p["jugadores"].index(p["turno"])
        p["turno"] = p["jugadores"][(idx+1) % len(p["jugadores"])]
        p["turno_inicio"] = time.time()
        p["pasadas"] += 1
        if p["pasadas"] >= len(p["jugadores"]):
            terminar_partida(mesa_id, tranca=True)
    return p

def terminar_partida(mesa_id, tranca=False):
    p = PARTIDAS.get(mesa_id)
    if not p:
        return
    mesa = MESAS[mesa_id]
    apuesta = mesa["apuesta"]
    ganador = None
    menor = 999
    for uid in p["jugadores"]:
        mano = p["manos"].get(str(uid), [])
        if len(mano) == 0:
            ganador = uid
            break
        pts = sum(sum(f) for f in mano)
        if pts < menor:
            menor = pts
            ganador = uid
    p["terminada"] = True
    p["ganador"] = ganador
    premio = apuesta * (len(p["jugadores"])-1)
    add_saldo(ganador, premio)
    expulsados = []
    quedan = []
    for uid in p["jugadores"]:
        if uid == ganador:
            quedan.append(uid)
        else:
            if saldo(uid) < apuesta:
                expulsados.append(uid)
            else:
                quedan.append(uid)
    mesa["jugadores"] = quedan
    p["expulsados"] = expulsados
    if len(quedan) < 2:
        mesa["jugadores"] = []
    return p

# ============ WEB ============
@app.route("/")
def index():
    return HTML

@app.errorhandler(404)
def not_found_404(e):
    return HTML

@app.route("/api/estado")
def estado():
    uid = request.args.get("uid", "")
    return jsonify({
        "saldo": saldo(uid),
        "mesas": [{"id": m["id"], "nombre": m["nombre"], "apuesta": m["apuesta"], "jugadores": len(m["jugadores"]), "max": 4} for m in MESAS.values()],
        "usuarios": USUARIOS,
        "tarjeta": TARJETA,
        "movil": MOVIL_CONFIRMAR,
        "group_id": GROUP_ID
    })

@app.route("/api/entrar_mesa", methods=["POST"])
def entrar_mesa():
    d = request.json
    uid = str(d.get("uid")); mesa_id = d.get("mesa_id")
    nombre = d.get("nombre", "Jugador")
    USUARIOS.setdefault(uid, {"nombre": nombre, "saldo": 0})
    USUARIOS[uid]["nombre"] = nombre
    mesa = MESAS.get(mesa_id)
    if not mesa:
        return jsonify({"ok": False, "msg": "Mesa no existe"})
    if uid in mesa["jugadores"]:
        return jsonify({"ok": True})
    if len(mesa["jugadores"]) >= 4:
        return jsonify({"ok": False, "msg": "Mesa llena"})
    if saldo(uid) < mesa["apuesta"]:
        return jsonify({"ok": False, "msg": "No tienes fichas suficientes para esta mesa. Recarga."})
    USUARIOS[uid]["saldo"] -= mesa["apuesta"]
    mesa["jugadores"].append(uid)
    if len(mesa["jugadores"]) >= 2:
        if mesa_id not in PARTIDAS or PARTIDAS[mesa_id].get("terminada"):
            iniciar_partida(mesa_id)
    return jsonify({"ok": True})

@app.route("/api/mesa")
def api_mesa():
    mesa_id = request.args.get("mesa_id")
    uid = request.args.get("uid", "")
    p = PARTIDAS.get(mesa_id)
    if p:
        verificar_timeout(mesa_id)
        p = PARTIDAS.get(mesa_id)
        tiempo_restante = max(0, 30 - int(time.time() - p["turno_inicio"])) if not p["terminada"] else 0
    else:
        tiempo_restante = 30
    mesa = MESAS.get(mesa_id, {"jugadores": []})
    return jsonify({
        "partida": p,
        "mesa": {"jugadores": mesa["jugadores"], "apuesta": mesa.get("apuesta", 0)},
        "mi_mano": p["manos"].get(str(uid), []) if p else [],
        "tiempo_restante": tiempo_restante,
        "mi_saldo": saldo(uid),
        "expulsado": (p and str(uid) in [str(x) for x in p.get("expulsados", [])])
    })

@app.route("/api/jugar", methods=["POST"])
def jugar():
    d = request.json
    mesa_id = d.get("mesa_id"); uid = str(d.get("uid")); ficha = d.get("ficha"); lado = d.get("lado", "der")
    p = PARTIDAS.get(mesa_id)
    if not p or p["terminada"]:
        return jsonify({"ok": False, "msg": "No hay partida"})
    verificar_timeout(mesa_id)
    if str(p["turno"]) != uid:
        return jsonify({"ok": False, "msg": "No es tu turno"})
    mano = p["manos"].get(uid, [])
    if ficha not in mano and [ficha[1], ficha[0]] not in mano:
        return jsonify({"ok": False, "msg": "No tienes esa ficha"})
    if ficha in mano:
        mano.remove(ficha)
    else:
        ficha = [ficha[1], ficha[0]]
        mano.remove(ficha)
    if not p["mesa_fichas"]:
        p["mesa_fichas"].append(ficha)
        p["extremo_izq"] = ficha[0]; p["extremo_der"] = ficha[1]
    else:
        if lado == "izq":
            if ficha[1] == p["extremo_izq"]:
                p["mesa_fichas"].insert(0, ficha); p["extremo_izq"] = ficha[0]
            elif ficha[0] == p["extremo_izq"]:
                p["mesa_fichas"].insert(0, [ficha[1], ficha[0]]); p["extremo_izq"] = ficha[1]
            else:
                mano.append(ficha)
                return jsonify({"ok": False, "msg": "No encaja ahí"})
        else:
            if ficha[0] == p["extremo_der"]:
                p["mesa_fichas"].append(ficha); p["extremo_der"] = ficha[1]
            elif ficha[1] == p["extremo_der"]:
                p["mesa_fichas"].append([ficha[1], ficha[0]]); p["extremo_der"] = ficha[0]
            else:
                mano.append(ficha)
                return jsonify({"ok": False, "msg": "No encaja ahí"})
    p["pasadas"] = 0
    if len(mano) == 0:
        terminar_partida(mesa_id)
        return jsonify({"ok": True, "gano": True})
    idx = p["jugadores"].index(p["turno"])
    p["turno"] = p["jugadores"][(idx+1) % len(p["jugadores"])]
    p["turno_inicio"] = time.time()
    return jsonify({"ok": True})

@app.route("/api/pasar", methods=["POST"])
def pasar():
    d = request.json
    mesa_id = d.get("mesa_id"); uid = str(d.get("uid"))
    p = PARTIDAS.get(mesa_id)
    if not p or str(p["turno"]) != uid:
        return jsonify({"ok": False})
    idx = p["jugadores"].index(p["turno"])
    p["turno"] = p["jugadores"][(idx+1) % len(p["jugadores"])]
    p["turno_inicio"] = time.time()
    p["pasadas"] += 1
    if p["pasadas"] >= len(p["jugadores"]):
        terminar_partida(mesa_id, tranca=True)
    return jsonify({"ok": True})

@app.route("/api/recargar", methods=["POST"])
def recargar():
    d = request.json
    uid = str(d.get("uid")); cantidad = d.get("cantidad"); tipo = d.get("tipo", "CUP")
    nombre = d.get("nombre", "Jugador")
    USUARIOS.setdefault(uid, {"nombre": nombre, "saldo": 0})
    pedido_id = f"REC-{int(time.time())}-{uid[-4:]}"
    PEDIDOS[pedido_id] = {"uid": uid, "cantidad": cantidad, "tipo": tipo, "nombre": nombre}
    callback = f"confirmar|{uid}|{cantidad}|{tipo}|{pedido_id}"
    callback_rech = f"rechazar|{uid}|{cantidad}|{tipo}|{pedido_id}"
    texto = f"🧾 NUEVO PEDIDO\n\n👤 {nombre}\n🆔 {uid}\n💰 {cantidad} fichas - {tipo}\n📋 {pedido_id}\n\nRevisa la transferencia a:\n💳 {TARJETA}\n📱 Confirmar: {MOVIL_CONFIRMAR}"
    # SIEMPRE manda al grupo, con el ID fijo
    r = tg("sendMessage", {"chat_id": GROUP_ID, "text": texto, "reply_markup": {"inline_keyboard": [[{"text": "✅ CONFIRMAR", "callback_data": callback}, {"text": "❌ RECHAZAR", "callback_data": callback_rech}]]}})
    print("RECARGA ENVIADA A GRUPO", GROUP_ID, r)
    return jsonify({"ok": True, "pedido_id": pedido_id, "tg": r})

@app.route("/api/test_grupo")
def test_grupo():
    r = tg("sendMessage", {"chat_id": GROUP_ID, "text": "🔔 Prueba: el bot sí puede mandar al grupo privado."})
    return jsonify({"group_id": GROUP_ID, "tg": r})

# ============ TELEGRAM WEBHOOK ============
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.json or {}
    if "callback_query" in update:
        cq = update["callback_query"]
        data = cq.get("data", "")
        cb_id = cq.get("id")
        chat_id = cq.get("message", {}).get("chat", {}).get("id")
        msg_id = cq.get("message", {}).get("message_id")
        try:
            tg("answerCallbackQuery", {"callback_query_id": cb_id, "text": "Procesando..."})
        except:
            pass
        try:
            partes = data.split("|")
            accion = partes[0] if partes else ""
            if accion in ("confirmar", "rechazar") and len(partes) >= 5:
                _, uid, cantidad, tipo, pedido_id = partes[:5]
                cantidad = int(float(cantidad))
                if accion == "confirmar":
                    add_saldo(uid, cantidad)
                    nuevo_texto = f"✅ CONFIRMADO\n\n👤 ID: {uid}\n💰 {cantidad} fichas - {tipo}\n📋 {pedido_id}\nNuevo saldo: {saldo(uid)}"
                    try:
                        tg("sendMessage", {"chat_id": uid, "text": f"✅ Tu recarga de {cantidad} fichas fue confirmada. Tu nuevo saldo es {saldo(uid)}."})
                    except:
                        pass
                else:
                    nuevo_texto = f"❌ RECHAZADO\n\n👤 ID: {uid}\n💰 {cantidad} fichas - {tipo}\n📋 {pedido_id}"
                    try:
                        tg("sendMessage", {"chat_id": uid, "text": "❌ Tu recarga fue rechazada. Revisa la transferencia y vuelve a intentar."})
                    except:
                        pass
                editado = False
                if chat_id and msg_id:
                    r = tg("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": nuevo_texto})
                    if r.get("ok"):
                        editado = True
                    else:
                        r2 = tg("editMessageCaption", {"chat_id": chat_id, "message_id": msg_id, "caption": nuevo_texto})
                        if r2.get("ok"):
                            editado = True
                if not editado and chat_id:
                    tg("sendMessage", {"chat_id": chat_id, "text": nuevo_texto})
                try:
                    tg("answerCallbackQuery", {"callback_query_id": cb_id, "text": "✅ Listo"})
                except:
                    pass
        except Exception as e:
            print("CALLBACK ERROR", e)
            if chat_id:
                tg("sendMessage", {"chat_id": chat_id, "text": f"Error procesando: {e}"})
        return jsonify({"ok": True})
    if "message" in update:
        msg = update["message"]
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "")
        if text.startswith("/start"):
            tg("sendMessage", {"chat_id": chat_id, "text": "🎲 Bienvenido al Club Dominó. Entra al juego y recarga desde la app."})
        elif text.startswith("/saldo"):
            tg("sendMessage", {"chat_id": chat_id, "text": f"Tu saldo es: {saldo(chat_id)} fichas."})
    return jsonify({"ok": True})

@app.route("/set_webhook")
def set_webhook():
    url = f"{BASE_URL}/webhook"
    r = requests.get(f"{TELEGRAM_API}/setWebhook?url={url}")
    return jsonify(r.json())

# ============ HTML ============
HTML = r"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Club Dominó</title>
<style>
*{box-sizing:border-box} body{margin:0;font-family:Arial;background:#0f3d2e;color:white}
.top{background:#0a2a1f;padding:10px;display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:900;font-size:20px;display:flex;align-items:center;gap:6px}
/* D ARREGLADA: circulo rojo simple, sin punteado, sin parecer poker */
.chip-D{width:22px;height:22px;min-width:22px;border-radius:50%;background:#d60000;border:2px solid #fff;display:inline-flex;align-items:center;justify-content:center;font-weight:900;font-size:13px;color:white;line-height:1}
.saldo{background:#ffd700;color:#000;padding:6px 10px;border-radius:20px;font-weight:900;display:flex;align-items:center;gap:5px}
.mesas{padding:10px;display:grid;grid-template-columns:1fr 1fr;gap:10px}
.mesa-card{background:#1a5c42;padding:12px;border-radius:12px;text-align:center;cursor:pointer}
.mesa-card b{font-size:20px}
.mesa-juego{background:#7a4a1f;padding:10px;border-radius:12px;margin:10px}
.pano{background:radial-gradient(circle,#1e9e5a,#0d5a2e);border-radius:10px;min-height:340px;padding:10px;position:relative;box-shadow:inset 0 0 30px rgba(0,0,0,.4)}
.timer{position:absolute;top:8px;right:10px;background:#000;color:#ffd700;padding:5px 10px;border-radius:20px;font-weight:900;font-size:16px}
.jugadores-top{display:flex;justify-content:space-around;font-size:12px;margin-bottom:8px}
.tablero{display:flex;flex-direction:column;align-items:center;gap:2px;min-height:200px;max-height:240px;overflow:auto}
.ficha-domino{width:28px;height:52px;background:linear-gradient(180deg,#fdf6d8,#e8d9a8);border:1px solid #8a7a4a;border-radius:5px;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 1px 3px rgba(0,0,0,.4);flex-shrink:0}
.ficha-domino.horizontal{width:52px;height:28px;flex-direction:row}
.mitad{flex:1;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(3,1fr);width:100%;height:100%;padding:2px}
.divisor{width:80%;height:1px;background:#8a7a4a}
.ficha-domino.horizontal .divisor{width:1px;height:80%}
.punto{width:5px;height:5px;background:#111;border-radius:50%;justify-self:center;align-self:center}
.punto.p1{grid-column:2;grid-row:2}
.punto.p2a{grid-column:1;grid-row:1}.punto.p2b{grid-column:3;grid-row:3}
.punto.p3a{grid-column:1;grid-row:1}.punto.p3b{grid-column:2;grid-row:2}.punto.p3c{grid-column:3;grid-row:3}
.punto.p4a{grid-column:1;grid-row:1}.punto.p4b{grid-column:3;grid-row:1}.punto.p4c{grid-column:1;grid-row:3}.punto.p4d{grid-column:3;grid-row:3}
.punto.p5a{grid-column:1;grid-row:1}.punto.p5b{grid-column:3;grid-row:1}.punto.p5c{grid-column:2;grid-row:2}.punto.p5d{grid-column:1;grid-row:3}.punto.p5e{grid-column:3;grid-row:3}
.punto.p6a{grid-column:1;grid-row:1}.punto.p6b{grid-column:3;grid-row:1}.punto.p6c{grid-column:1;grid-row:2}.punto.p6d{grid-column:3;grid-row:2}.punto.p6e{grid-column:1;grid-row:3}.punto.p6f{grid-column:3;grid-row:3}
.mi-mano{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-top:10px}
.mi-mano .ficha-domino{width:34px;height:62px;cursor:pointer}
.mi-mano .ficha-domino.seleccionada{outline:3px solid #ffd700;transform:translateY(-6px)}
.btn{background:#ffd700;color:#000;border:none;padding:11px 16px;border-radius:10px;font-weight:900;width:100%;margin-top:8px;font-size:16px}
/* RECARGA CON APARTADOS SEPARADOS */
.recarga-wrap{padding:10px;display:flex;flex-direction:column;gap:8px}
.caja{background:#fff3a0;color:#111;border-radius:12px;padding:12px;text-align:center}
.caja-blanca{background:#ffffff;color:#111;border-radius:10px;padding:10px;margin-top:6px}
.caja-blanca small{color:#555;font-size:12px}
.caja-blanca b.num{font-size:19px;letter-spacing:1px}
input{width:100%;padding:11px;border-radius:8px;border:1px solid #ccc;margin:0;font-size:16px;text-align:center}
.hidden{display:none}
</style></head>
<body>
<div class="top"><div class="logo">🎲 CLUB DOMINÓ <span class="chip-D">D</span></div><div class="saldo">💰 <span id="saldo">0</span> <span class="chip-D">D</span></div></div>

<div id="vista-lobby">
<div class="recarga-wrap">
  <div class="caja">
    <div style="font-weight:900;font-size:16px">💳 RECARGAR</div>
    <div class="caja-blanca"><small>Tarjeta CUP</small><br><b class="num">9238-1299-7507-3018</b></div>
    <div class="caja-blanca"><small>📱 Móvil a confirmar</small><br><b class="num">55348244</b></div>
  </div>
  <div class="caja">
    <div style="font-weight:900;margin-bottom:6px">Cantidad de fichas</div>
    <input id="cantRec" type="number" placeholder="Ej: 100" value="100">
    <button class="btn" onclick="recargar()">ENVIAR</button>
    <div id="msgRec" style="font-size:13px;margin-top:6px"></div>
  </div>
</div>
<div style="padding:0 10px"><b>Mesas - Elige una:</b></div>
<div class="mesas" id="listaMesas"></div>
</div>

<div id="vista-juego" class="hidden">
<div class="mesa-juego"><div style="display:flex;justify-content:space-between"><b id="nombreMesa">Mesa</b><button onclick="salir()" style="background:#fff;border:none;border-radius:8px;padding:5px 10px">Salir</button></div>
<div class="pano">
<div class="timer" id="timer">⏱ 30s</div>
<div class="jugadores-top" id="jugTop"></div>
<div class="tablero" id="tablero"></div>
<div id="turnoTxt" style="text-align:center;margin-top:8px;font-weight:900"></div>
<div class="mi-mano" id="miMano"></div>
<button class="btn" onclick="pasar()">PASAR TURNO</button>
<div id="msgJuego" style="text-align:center;margin-top:6px"></div>
</div></div></div>

<script>
let UID = localStorage.getItem("uid") || ("U"+Math.floor(Math.random()*999999));
localStorage.setItem("uid", UID);
let NOMBRE = localStorage.getItem("nombre") || prompt("Tu nombre:") || "Jugador";
localStorage.setItem("nombre", NOMBRE);
let MESA = null, SEL = null, TIMER_INT = null;
function puntosHTML(n){
  if(n==0) return '<div class="mitad"></div>';
  let map={1:['p1'],2:['p2a','p2b'],3:['p3a','p3b','p3c'],4:['p4a','p4b','p4c','p4d'],5:['p5a','p5b','p5c','p5d','p5e'],6:['p6a','p6b','p6c','p6d','p6e','p6f']};
  return '<div class="mitad">'+map[n].map(c=>'<div class="punto '+c+'"></div>').join('')+'</div>';
}
function fichaHTML(f, horiz){
  return '<div class="ficha-domino '+(horiz?'horizontal':'')+'">'+puntosHTML(f[0])+'<div class="divisor"></div>'+puntosHTML(f[1])+'</div>';
}
async function cargar(){
  let r = await fetch('/api/estado?uid='+UID); let d = await r.json();
  document.getElementById('saldo').innerText = d.saldo;
  let h='';
  d.mesas.forEach(m=>{ h+='<div class="mesa-card" onclick="entrar(\''+m.id+'\')"><b>'+m.apuesta+' <span style="font-size:12px">fichas</span></b><br>'+m.nombre+'<br>👥 '+m.jugadores+'/4<br><span style="background:#ffd700;color:#000;padding:2px 8px;border-radius:10px;font-size:12px">ENTRAR</span></div>' });
  document.getElementById('listaMesas').innerHTML=h;
}
async function entrar(mid){
  let r = await fetch('/api/entrar_mesa',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({uid:UID,mesa_id:mid,nombre:NOMBRE})});
  let d = await r.json();
  if(!d.ok){ alert(d.msg); return; }
  MESA=mid; document.getElementById('vista-lobby').classList.add('hidden'); document.getElementById('vista-juego').classList.remove('hidden');
  document.getElementById('nombreMesa').innerText = 'Mesa '+mid;
  actualizar();
  TIMER_INT=setInterval(actualizar, 1000);
}
function salir(){ clearInterval(TIMER_INT); location.reload(); }
async function recargar(){
  let cant=document.getElementById('cantRec').value;
  if(!cant||cant<=0){ alert('Pon cantidad'); return; }
  let r=await fetch('/api/recargar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({uid:UID,cantidad:parseInt(cant),tipo:'CUP',nombre:NOMBRE})});
  let d=await r.json();
  document.getElementById('msgRec').innerText='✅ Pedido enviado. Transfiere a 9238-1299-7507-3018 y espera confirmación en el grupo. Pedido: '+d.pedido_id;
}
async function actualizar(){
  if(!MESA) return;
  let r=await fetch('/api/mesa?mesa_id='+MESA+'&uid='+UID); let d=await r.json();
  document.getElementById('saldo').innerText=d.mi_saldo;
  if(d.expulsado){ alert('Te quedaste sin fichas para esta mesa. La mesa te expulsó. Recarga para volver a jugar.'); salir(); return; }
  let p=d.partida;
  if(!p){ document.getElementById('tablero').innerHTML='<div style="text-align:center">Esperando jugadores...</div>'; return; }
  document.getElementById('timer').innerText='⏱ '+d.tiempo_restante+'s';
  let jugHtml = p.jugadores.map(u=> (u==p.turno?'🟢 ':'')+(u==UID?'TÚ':u)+' ('+(p.manos[u]?p.manos[u].length:0)+')').join(' | ');
  document.getElementById('jugTop').innerHTML=jugHtml;
  let tab = p.mesa_fichas.map((f,i)=> fichaHTML(f, i%3==1)).join('');
  document.getElementById('tablero').innerHTML=tab || '<div>Sin fichas aún</div>';
  document.getElementById('turnoTxt').innerText = p.terminada ? ('🏆 Ganó: '+(p.ganador==UID?'TÚ':p.ganador)) : (p.turno==UID ? 'TE TOCA A TI - ¡Juega!' : 'Le toca a '+(p.turno==UID?'TI':p.turno));
  let manoHtml = d.mi_mano.map((f,i)=> '<div onclick="selFicha('+i+')" id="f'+i+'">'+fichaHTML(f,false)+'</div>').join('');
  document.getElementById('miMano').innerHTML=manoHtml;
  if(p.terminada){ document.getElementById('msgJuego').innerText='Mano terminada. Si tienes fichas, quédate para la próxima. Si no, recarga.'; }
}
function selFicha(i){
  fetch('/api/mesa?mesa_id='+MESA+'&uid='+UID).then(r=>r.json()).then(d=>{
    let f=d.mi_mano[i]; SEL=f;
    document.querySelectorAll('#miMano > div').forEach(el=>el.classList.remove('seleccionada'));
    document.getElementById('f'+i).classList.add('seleccionada');
    jugarLado('der');
  });
}
async function jugarLado(lado){
  if(!SEL) return;
  let r=await fetch('/api/jugar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({uid:UID,mesa_id:MESA,ficha:SEL,lado:lado})});
  let d=await r.json();
  if(!d.ok && lado=='der'){
    let r2=await fetch('/api/jugar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({uid:UID,mesa_id:MESA,ficha:SEL,lado:'izq'})});
    let d2=await r2.json();
    if(!d2.ok) document.getElementById('msgJuego').innerText=d2.msg;
  } else if(!d.ok){ document.getElementById('msgJuego').innerText=d.msg; }
  SEL=null; actualizar();
}
async function pasar(){
  await fetch('/api/pasar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({uid:UID,mesa_id:MESA})});
  actualizar();
}
cargar();
</script></body></html>
"""

@app.route("/Cubadomino")
@app.route("/cubadomino")
@app.route("/Cubadomino/")
def cubadomino():
    return HTML

@app.route("/<path:ruta_cualquiera>")
def ruta_cualquiera(ruta_cualquiera):
    if ruta_cualquiera.startswith("api/") or ruta_cualquiera.startswith("webhook") or ruta_cualquiera.startswith("set_webhook"):
        return "Not Found", 404
    return HTML

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
