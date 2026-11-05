import os, json, urllib.request
from flask import Flask, Response, request, jsonify

app = Flask(__name__)

GROUP_ID = "-1004353226044"
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

def enviar_a_grupo(texto):
    if not BOT_TOKEN:
        print("Falta BOT_TOKEN")
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": GROUP_ID, "text": texto, "parse_mode": "HTML"}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print("Error grupo:", e)
        return False

@app.route("/api/solicitud", methods=["POST"])
def solicitud():
    d = request.get_json(force=True)
    tipo = d.get("tipo","RECARGA")
    usuario = d.get("usuario","Carlos M.")
    cantidad = d.get("cantidad","")
    if tipo == "RECARGA":
        msg = f"💰 <b>NUEVA RECARGA</b>\n\n👤 Usuario: {usuario}\n🪙 Fichas: {cantidad}\n💳 Pagó a: 9238-1299-7507-3018\n📲 Móvil a confirmar: 55348244\n\n📸 <b>Esperando captura de transferencia</b>\n✅ Aprueba y agrégale las fichas."
    else:
        msg = f"⬇️ <b>NUEVO RETIRO / VENTA</b>\n\n👤 Usuario: {usuario}\n🪙 Fichas que vende: {cantidad}\n💳 SU tarjeta: {d.get('tarjeta','')}\n📲 SU móvil: {d.get('movil','')}\n\n💸 Págalo a SU tarjeta y descuéntale las fichas."
    enviar_a_grupo(msg)
    return jsonify({"ok": True})

HTML = r"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Club de Dominó Cubano</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
*{box-sizing:border-box;font-family:'Segoe UI',Arial,sans-serif} body{margin:0;background:#0a2e1f;color:#fff;padding-bottom:80px}
.top{background:#053a24;padding:12px 14px;display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #f5c518;position:sticky;top:0;z-index:10}
.logo{font-size:17px;font-weight:900;line-height:1.1;color:#f5c518}.logo small{color:#fff;font-size:11px;letter-spacing:1px;font-weight:400}
.saldoBox{background:#000;border:1px solid #f5c518;border-radius:10px;padding:6px 10px;text-align:right;font-size:11px}.saldoBox b{font-size:18px;color:#f5c518}
.btnR{background:#22c55e;color:#fff;border:0;padding:10px 14px;border-radius:10px;font-weight:900;cursor:pointer}
.wrap{padding:12px} h1{font-size:26px;margin:4px 0}.sub{opacity:.85;font-size:13px;margin:0 0 12px}
.iaCard{background:linear-gradient(135deg,#f5c518,#b8860b);color:#000;border-radius:18px;padding:14px;margin-bottom:14px}.iaCard h2{margin:0;font-size:20px}
.btnIA{background:#000;color:#f5c518;border:0;padding:13px;border-radius:12px;width:100%;font-weight:900;font-size:16px;cursor:pointer}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(min-width:700px){.grid{grid-template-columns:repeat(4,1fr)}}
.card{background:#0f3a26;border:1px solid #2a5a3d;border-radius:16px;padding:12px}
.card h3{margin:0;color:#f5c518;font-size:13px}.card h3 span{display:inline-block;background:#22c55e;color:#fff;font-size:10px;padding:2px 7px;border-radius:10px;margin-top:4px}
.card h3 span.naranja{background:#eab308;color:#000}.card h3 span.rojo{background:#ef4444}.card h3 span.dorado{background:#f5c518;color:#000}
.mini{display:flex;gap:3px;margin:10px 0;justify-content:center}
.mDom{background:#fff;width:18px;height:34px;border-radius:4px;display:flex;flex-direction:column;overflow:hidden;border:1px solid #999}
.mDom div{flex:1;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(3,1fr);padding:2px}.mDom div:first-child{border-bottom:1px solid #111}
.dot{width:3px;height:3px;background:#111;border-radius:50%;place-self:center}
.info{font-size:12px;opacity:.9;text-align:center;margin:6px 0}
.btn{width:100%;background:#22c55e;color:#fff;border:0;padding:11px;border-radius:10px;font-weight:900;cursor:pointer}
.mesa{background:radial-gradient(circle at 50% 30%,#1a6b3a,#0a3d1f 70%);border:6px solid #5a3a1a;border-radius:22px;min-height:200px;padding:12px;display:flex;flex-wrap:wrap;gap:8px;justify-content:center;align-content:center}
.ficha{background:#fff;border-radius:9px;width:48px;height:92px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 4px 10px #0006;cursor:pointer}
.ficha .mitad{flex:1;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(3,1fr);padding:4px}.ficha .mitad:first-child{border-bottom:2px solid #111}
.punto{width:9px;height:9px;background:#111;border-radius:50%;place-self:center}
.ficha.jugable{outline:3px solid #22c55e;transform:translateY(-6px)}
.ficha.enmesa{width:52px;height:96px;cursor:default}.ficha.enmesa.h{width:96px;height:52px;flex-direction:row}.ficha.enmesa.h .mitad:first-child{border-bottom:0;border-right:2px solid #111}
.mano{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.modal{position:fixed;inset:0;background:#000c;display:none;align-items:flex-end;justify-content:center;z-index:99}
.modal>div{background:#0f2a1c;width:100%;max-width:480px;border-radius:20px 20px 0 0;padding:18px;max-height:92vh;overflow:auto}
.inp{width:100%;padding:13px;border-radius:12px;border:1px solid #2a5a3d;background:#07120d;color:#fff;font-size:16px;margin:8px 0}
.tab{display:flex;gap:8px}.tab button{flex:1;padding:11px;border-radius:10px;border:0;font-weight:900;cursor:pointer}.tab button.on{background:#f5c518;color:#000}.tab button:not(.on){background:#222;color:#fff}
.copyBox{background:#07120d;border:1px dashed #f5c518;border-radius:14px;padding:12px;margin:10px 0;text-align:center}
.copyBox b{font-size:19px;letter-spacing:1px;color:#f5c518}.copyBox span{font-size:18px;font-weight:900}
.btnCopy{background:#f5c518;color:#000;border:0;padding:8px 14px;border-radius:8px;font-weight:900;cursor:pointer;margin-top:6px}
.nav{position:fixed;bottom:0;left:0;right:0;background:#000;display:flex;justify-content:space-around;padding:13px 0;border-top:1px solid #333;font-size:12px}.nav b{color:#f5c518}
.espera{background:#0f3a26;border-radius:16px;padding:16px;text-align:center;margin-top:10px}
</style></head>
<body>
<div class="top"><div class="logo">🀄 CLUB DE DOMINÓ CUBANO<br><small>LOBBY - MESAS DISPONIBLES</small></div>
<div style="display:flex;gap:8px;align-items:center"><div class="saldoBox">Jugador: Carlos M.<br>SALDO DE FICHAS<br><b id="saldo">12,450</b> FICHAS</div><button class="btnR" onclick="abrirRecarga()">+ RECARGAR</button></div></div>

<div class="wrap" id="lobby">
<h1>🀄 Lobby de Mesas</h1><p class="sub">Selecciona una mesa • 16 mesas activas + 1 IA • 42 jugadores en línea</p>
<div class="iaCard"><h2>🤖 MESA ESPECIAL - JUGAR CON IA</h2><p>Una sola mesa aparte. Juegas tú contra la máquina ahora mismo, sin esperar a nadie.</p><p><b>Apuesta: 5 fichas • 2 jugadores • Siempre disponible</b></p><button class="btnIA" onclick="entrarIA()">▶️ JUGAR CON IA AHORA</button></div>
<h2 style="color:#f5c518">👥 MESAS PARA PERSONAS REALES - 2 a 4 jugadores</h2><p class="sub">Para jugar aquí tienes que tener fichas recargadas. Mínimo 2 personas para empezar.</p>
<div class="grid" id="gridMesas"></div></div>

<div class="wrap" id="juego" style="display:none">
<button onclick="salir()" style="background:#222;color:#fff;border:1px solid #444;padding:10px 14px;border-radius:10px;cursor:pointer">← Lobby</button>
<h2 id="tituloMesa">Mesa IA</h2><div style="background:#f5c518;color:#000;text-align:center;padding:11px;border-radius:12px;font-weight:900" id="turno">Tu turno</div>
<div style="display:flex;justify-content:space-between;background:#0a1f14;padding:10px;border-radius:12px;margin:10px 0"><span>🤖 BOT - Máquina</span><b>🀄 <span id="botCount">7</span> fichas</b></div>
<div class="mesa" id="mesa"></div>
<div style="text-align:center;background:#000a;padding:10px;border-radius:10px;margin:10px 0">Extremos: <b id="extremos" style="color:#f5c518">-</b> | <span id="msg">Te repartimos 7 fichas.</span></div>
<div style="background:#0f2a1c;border-radius:16px;padding:12px"><p style="text-align:center;margin:0 0 10px"><b>TUS FICHAS - Toca una verde para jugar</b></p><div class="mano" id="mano"></div><div style="text-align:center;margin-top:12px"><button id="btnPasar" onclick="pasar()" style="display:none;background:#f5c518;color:#000;padding:11px 18px;border-radius:10px;font-weight:900;border:0">⏭️ PASAR</button> <button onclick="nuevaPartida()" style="background:#22c55e;color:#fff;padding:11px 18px;border-radius:10px;font-weight:900;border:0">🔄 NUEVA</button></div></div></div>

<div class="wrap" id="espera" style="display:none">
<button onclick="salir()" style="background:#222;color:#fff;border:1px solid #444;padding:10px 14px;border-radius:10px">← Lobby</button>
<div class="espera"><h2 id="esperaTitulo">Mesa #1021</h2><p style="font-size:50px;margin:10px">⏳</p><h3>1 / 4 jugadores</h3><p>Esperando a que entren más jugadores reales.<br>Mínimo 2 para empezar.</p><button class="btn" onclick="alert('Cuando entre otro jugador real, la partida empieza sola. Por ahora puedes practicar en la mesa de IA.')">🔔 AVISARME CUANDO SE LLENE</button></div></div>

<div class="modal" id="modalRecarga"><div>
<div style="display:flex;justify-content:space-between"><h2 style="margin:0">💰 Recargar / Retirar</h2><button onclick="cerrarRecarga()" style="background:#222;color:#fff;border:0;padding:8px 12px;border-radius:8px">✕</button></div>
<p style="opacity:.85;font-size:13px">Solo CUP por el momento. Saldo: <b id="saldo2" style="color:#f5c518">12,450</b> fichas</p>
<div class="tab"><button id="tabR" class="on" onclick="setTab('R')">⬆️ RECARGAR</button><button id="tabW" onclick="setTab('W')">⬇️ RETIRAR / VENDER</button></div>
<div id="pasoRecarga">
<p style="margin:12px 0 0">¿Cuántas fichas quieres comprar?</p>
<input class="inp" id="cantR" type="number" value="1000" min="100">
<p style="font-size:13px;opacity:.8">1 ficha = 1 CUP • Mínimo 100 fichas</p>
<button class="btn" onclick="mostrarDatos()">➡️ CONTINUAR - VER DATOS PARA TRANSFERIR</button>
<div id="datosPago" style="display:none">
<div style="background:#f5c518;color:#000;padding:12px;border-radius:12px;text-align:center;font-weight:900;margin-top:12px">TRANSFIERE AQUÍ 👇</div>
<div class="copyBox">📌 Tarjeta CUP:<br><b>9238-1299-7507-3018</b><br><button class="btnCopy" onclick="copiar('9238129975073018')">📋 COPIAR TARJETA</button></div>
<div class="copyBox">📲 Móvil a confirmar:<br><span>55348244</span><br><button class="btnCopy" onclick="copiar('55348244')">📋 COPIAR NÚMERO</button></div>
<div style="background:#07120d;padding:12px;border-radius:12px;font-size:13px;line-height:1.6"><b>Pasos:</b><br>1. Transfiere a esa tarjeta<br>2. Deja una captura 📸 de tu transferencia ✅<br>3. Toca el botón de abajo para enviarme la captura por WhatsApp<br>4. Yo apruebo y te agrego las fichas a tu cuenta</div>
<button class="btn" style="margin-top:12px;background:#25D366" onclick="enviarRecarga()">📸 ENVIAR CAPTURA POR WHATSAPP</button>
</div></div>
<div id="pasoRetiro" style="display:none">
<p style="margin:12px 0 0">¿Cuántas fichas me quieres vender?</p>
<input class="inp" id="cantW" type="number" value="1000" min="500">
<p style="font-size:13px;opacity:.8">Mínimo retiro: 500 fichas • 1 ficha = 1 CUP</p>
<p>Pon TU tarjeta CUP:</p><input class="inp" id="miTarjeta" placeholder="Ej: 9238-XXXX-XXXX-XXXX" maxlength="19">
<p>Pon TU número a confirmar:</p><input class="inp" id="miMovil" placeholder="Ej: 55XXXXXX" maxlength="8">
<button class="btn" style="background:#f5c518;color:#000" onclick="enviarRetiro()">➡️ SOLICITAR RETIRO POR WHATSAPP</button>
<div style="background:#07120d;padding:12px;border-radius:12px;font-size:13px;margin-top:10px;line-height:1.6">Yo reviso tu solicitud, te transfiero a TU tarjeta y te descuento las fichas de tu cuenta.</div>
</div>
<p id="resSolicitud" style="text-align:center;font-weight:800;color:#22c55e"></p>
</div></div>

<div class="nav"><span>🏠 <b>Lobby</b></span><span>🃏 Mis Mesas</span><span>🏆 Clasificación</span><span onclick="abrirRecarga()">🛒 Tienda</span></div>
<script>
let saldo=12450,apuesta=5,mazo=[],mano=[],bot=[],mesa=[],izq=null,der=null,miTurno=true,fin=false,tab='R';
const POS={0:[],1:[[1,1]],2:[[0,0],[2,2]],3:[[0,0],[1,1],[2,2]],4:[[0,0],[0,2],[2,0],[2,2]],5:[[0,0],[0,2],[1,1],[2,0],[2,2]],6:[[0,0],[0,2],[1,0],[1,2],[2,0],[2,2]]};
function puntos(n){let h='';POS[n].forEach(p=>{h+=`<i class="dot" style="grid-column:${p[1]+1};grid-row:${p[0]+1}"></i>`});return `<div class="mitad">${h}</div>`;}
function fichaHTML(f,clase="",h=false){return `<div class="ficha ${clase} ${h?'h':''}">${puntos(f[0])}${puntos(f[1])}</div>`;}
function miniDom(){let s='';let demo=[[6,6],[5,3],[4,4],[2,6],[1,5],[3,3],[0,6]];demo.forEach(f=>{s+=`<div class="mDom">${puntos(f[0])}${puntos(f[1])}</div>`});return `<div class="mini">${s}</div>`;}
let apuestas=[5,5,10,10,20,20,50,50,100,100,200,200,500,500,1000,1000];
let niveles={5:['Principiante',''],10:['Principiante',''],20:['Intermedio','naranja'],50:['Intermedio','naranja'],100:['Avanzado','rojo'],200:['Avanzado','rojo'],500:['VIP','dorado'],1000:['VIP','dorado']};
let ids=[1021,1022,1031,1032,1041,1042,1051,1052,1061,1062,1071,1072,1081,1082,1091,1092];
function renderMesas(){let g=document.getElementById('gridMesas');g.innerHTML='';apuestas.forEach((ap,i)=>{let jug=[2,3,1,4,2,3][i%6];let estado=jug>=4?'Ronda activa':'Esperando';g.innerHTML+=`<div class="card"><h3>MESAS DE ${ap} FICHAS<br><span class="${niveles[ap][1]}">Nivel: ${niveles[ap][0]}</span></h3>${miniDom()}<div class="info">👥 ${jug}/4 jugadores • ${estado}<br>Apuesta: ${ap} fichas • ${ap>=500?'Torneo':'Clásica'}</div><button class="btn" onclick="entrarReal(${ids[i]},${ap})">ENTRAR</button></div>`;});}
renderMesas();
function abrirRecarga(){document.getElementById('modalRecarga').style.display='flex';document.getElementById('saldo2').innerText=saldo.toLocaleString();}
function cerrarRecarga(){document.getElementById('modalRecarga').style.display='none';}
function setTab(t){tab=t;document.getElementById('tabR').className=t==='R'?'on':'';document.getElementById('tabW').className=t==='W'?'on':'';document.getElementById('pasoRecarga').style.display=t==='R'?'block':'none';document.getElementById('pasoRetiro').style.display=t==='W'?'block':'none';}
function copiar(txt){navigator.clipboard.writeText(txt).then(()=>alert('Copiado: '+txt));}
function mostrarDatos(){let c=parseInt(document.getElementById('cantR').value||0);if(c<100){alert('Mínimo de recarga: 100 fichas');return;}document.getElementById('datosPago').style.display='block';document.getElementById('datosPago').scrollIntoView({behavior:'smooth'});}
function enviarRecarga(){
  let c=document.getElementById('cantR').value;
  fetch('/api/solicitud',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tipo:'RECARGA',cantidad:c,usuario:'Carlos M.'})});
  let msg=encodeURIComponent('Hola Alvanis, quiero RECARGAR '+c+' fichas en Club de Dominó.\n\nYa transferí a tu tarjeta 9238-1299-7507-3018 (Móvil: 55348244).\nTe dejo la captura 📸 de mi transferencia ✅\nUsuario: Carlos M.');
  window.open('https://wa.me/5355348244?text='+msg,'_blank');
  document.getElementById('resSolicitud').innerText='✅ Solicitud enviada a tu grupo privado. Ahora mándame la captura por WhatsApp.';
}
function enviarRetiro(){
  let c=document.getElementById('cantW').value;
  let tar=document.getElementById('miTarjeta').value.trim();
  let mov=document.getElementById('miMovil').value.trim();
  if(parseInt(c)<500){alert('Mínimo de retiro: 500 fichas');return;}
  if(parseInt(c)>saldo){alert('No tienes tantas fichas. Tu saldo: '+saldo);return;}
  if(tar.length<10){alert('Pon tu tarjeta CUP completa');return;}
  if(mov.length<8){alert('Pon tu número a confirmar (8 dígitos)');return;}
  fetch('/api/solicitud',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tipo:'RETIRO',cantidad:c,usuario:'Carlos M.',tarjeta:tar,movil:mov})});
  let msg=encodeURIComponent('Hola Alvanis, quiero RETIRAR / VENDER '+c+' fichas.\n\nMI tarjeta CUP: '+tar+'\nMI móvil a confirmar: '+mov+'\nUsuario: Carlos M.');
  window.open('https://wa.me/5355348244?text='+msg,'_blank');
  document.getElementById('resSolicitud').innerText='✅ Retiro enviado a tu grupo privado. Te pago a tu tarjeta.';
}
function entrarReal(id,ap){if(saldo<ap){alert('No tienes suficientes fichas. Recarga con el administrador.');abrirRecarga();return;}document.getElementById('lobby').style.display='none';document.getElementById('juego').style.display='none';document.getElementById('espera').style.display='block';document.getElementById('esperaTitulo').innerText='Mesa #'+id+' - '+ap+' fichas';window.scrollTo(0,0);}
function entrarIA(){apuesta=5;document.getElementById('lobby').style.display='none';document.getElementById('espera').style.display='none';document.getElementById('juego').style.display='block';document.getElementById('tituloMesa').innerText='🤖 Mesa IA - 5 fichas';nuevaPartida();window.scrollTo(0,0);}
function salir(){document.getElementById('juego').style.display='none';document.getElementById('espera').style.display='none';document.getElementById('lobby').style.display='block';}
function crearMazo(){mazo=[];for(let a=0;a<=6;a++)for(let b=a;b<=6;b++)mazo.push([a,b]);}
function mezclar(){for(let i=mazo.length-1;i>0;i--){let j=Math.floor(Math.random()*(i+1));[mazo[i],mazo[j]]=[mazo[j],mazo[i]];}}
function nuevaPartida(){crearMazo();mezclar();mano=mazo.slice(0,7);bot=mazo.slice(7,14);mesa=[];izq=null;der=null;miTurno=true;fin=false;document.getElementById('msg').innerText='Te repartimos 7 fichas. Tú sales.';render();}
function puedeJugar(f){if(!mesa.length) return true;return f[0]===izq||f[1]===izq||f[0]===der||f[1]===der;}
function render(){document.getElementById('saldo').innerText=saldo.toLocaleString();document.getElementById('botCount').innerText=bot.length;document.getElementById('extremos').innerText=mesa.length?izq+' | '+der:'-';document.getElementById('turno').innerText=fin?'🏁 Partida terminada':(miTurno?'✅ TU TURNO - Toca una ficha verde':'⏳ Turno del BOT...');document.getElementById('mesa').innerHTML=mesa.length?mesa.map((f,i)=>fichaHTML(f,'enmesa',i%2===1)).join(''):'<p style="opacity:.8">Mesa vacía. Tira tu primera ficha.</p>';document.getElementById('mano').innerHTML=mano.map((f,i)=>{let ok=miTurno&&!fin&&puedeJugar(f);return `<div onclick="jugar(${i})">${fichaHTML(f,ok?'jugable':'')}</div>`}).join('');document.getElementById('btnPasar').style.display=(miTurno&&!fin&&mesa.length>0&&!mano.some(puedeJugar))?'inline-block':'none';}
function colocar(f,lado){if(!mesa.length){mesa.push(f);izq=f[0];der=f[1];return;}if(lado==='izq'){if(f[1]===izq){mesa.unshift(f);izq=f[0];}else{mesa.unshift([f[1],f[0]]);izq=f[1];}}else{if(f[0]===der){mesa.push(f);der=f[1];}else{mesa.push([f[1],f[0]]);der=f[0];}}}
function jugar(i){if(!miTurno||fin) return;let f=mano[i];if(!puedeJugar(f)){document.getElementById('msg').innerText='Esa no pega. Necesitas '+izq+' o '+der;return;}mano.splice(i,1);if(!mesa.length) colocar(f,'izq');else if(f[0]===izq||f[1]===izq) colocar(f,'izq');else colocar(f,'der');document.getElementById('msg').innerText='Jugaste ['+f[0]+'|'+f[1]+']';if(!mano.length){ganar(true);return;}miTurno=false;render();setTimeout(turnoBot,900);}
function turnoBot(){if(fin) return;let idx=bot.findIndex(puedeJugar);if(idx===-1){document.getElementById('msg').innerText='El BOT pasó. Te toca.';miTurno=true;render();verificarTranca();return;}let f=bot.splice(idx,1)[0];if(!mesa.length) colocar(f,'izq');else if(f[0]===izq||f[1]===izq) colocar(f,'izq');else colocar(f,'der');document.getElementById('msg').innerText='BOT jugó ['+f[0]+'|'+f[1]+']';if(!bot.length){ganar(false);return;}miTurno=true;render();verificarTranca();}
function pasar(){if(!miTurno||fin) return;miTurno=false;render();setTimeout(turnoBot,700);}
function verificarTranca(){if(mano.some(puedeJugar)||bot.some(puedeJugar)) return;let mp=mano.reduce((s,f)=>s+f[0]+f[1],0),bp=bot.reduce((s,f)=>s+f[0]+f[1],0);if(mp<bp) ganar(true,true);else if(bp<mp) ganar(false,true);else{fin=true;document.getElementById('msg').innerText='EMPATE - Tranca.';render();}}
function ganar(yo,tranca=false){fin=true;if(yo){saldo+=apuesta;document.getElementById('msg').innerText=(tranca?'¡TRANCA! GANASTE ':'¡GANASTE! ')+'+'+apuesta;}else{saldo=Math.max(0,saldo-apuesta);document.getElementById('msg').innerText=(tranca?'TRANCA - Perdiste. ':'PERDISTE. ')+'-'+apuesta;}render();setTimeout(()=>alert(document.getElementById('msg').innerText+'\nSaldo: '+saldo),300);}
try{Telegram.WebApp.ready();Telegram.WebApp.expand();}catch(e){}
</script></body></html>
"""

@app.route("/")
def index():
    return "Club de Domino - OK"

@app.route("/app")
def app_page():
    return Response(HTML, mimetype="text/html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
