import os
from flask import Flask, Response

app = Flask(__name__)

HTML = r"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Club de Dominó Cubano</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
*{box-sizing:border-box;font-family:Arial,sans-serif}
body{margin:0;background:#0b3d2a;color:#fff}
.top{background:#f5c518;color:#000;padding:10px;display:flex;justify-content:space-between;align-items:center}
.top b{font-size:20px;line-height:1}
.saldo{background:#000;color:#fff;padding:8px 12px;border-radius:10px;text-align:center;font-size:13px}
.saldo span{font-size:20px;font-weight:900}
.btn{background:#22c55e;color:#fff;border:0;padding:10px 14px;border-radius:10px;font-weight:900;cursor:pointer}
.wrap{padding:12px;padding-bottom:90px}
.card{background:#14532d;border:1px solid #f5c518;border-radius:16px;padding:12px;margin-bottom:12px}
.card h2{margin:4px 0;color:#f5c518}
.mesa{background:#0a2e1f;border:2px solid #f5c518;border-radius:16px;min-height:180px;padding:10px;display:flex;flex-wrap:wrap;gap:6px;align-content:flex-start}
.ficha{background:#fff;color:#000;width:44px;height:80px;border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;border:2px solid #000;cursor:pointer;user-select:none}
.ficha span{font-size:22px;font-weight:900;line-height:1}
.ficha hr{width:80%;border:1px solid #000;margin:4px 0}
.ficha.jugable{outline:3px solid #22c55e;transform:translateY(-4px)}
.ficha.enmesa{width:52px;height:88px;cursor:default}
.ficha.enmesa.h{width:88px;height:52px;flex-direction:row}
.ficha.enmesa.h hr{width:1px;height:70%;margin:0 4px}
.mano{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:10px}
.info{background:#0008;padding:10px;border-radius:10px;text-align:center;margin:8px 0}
.oculto{display:none}
.nav{position:fixed;bottom:0;left:0;right:0;background:#000;display:flex;justify-content:space-around;padding:12px}
.nav b{color:#fff}
</style></head>
<body>
<div class="top"><div><b>CLUB DE<br>DOMINÓ<br>CUBANO</b><br><small>LOBBY - MESAS</small></div>
<div class="saldo">Jugador: Carlos M.<br>SALDO<br><span id="saldo">12450</span> FICHAS</div>
<button class="btn" onclick="alert('Recarga pronto disponible')">+ RECARGAR</button></div>

<div class="wrap" id="lobby">
<h1>Lobby de Mesas</h1><p>Selecciona una mesa • Mesas en vivo • Juegan 2, 3 o 4</p>
<div class="card"><h2>MESAS DE 5 FICHAS</h2><p>Mesa #1021 • 2 jugadores • En vivo<br>Si hay 2, ya juega</p><p>Apuesta: 5 fichas</p><button class="btn" style="width:100%" onclick="entrarMesa(1021,5)">ENTRAR - JUGAR DE VERDAD</button></div>
<div class="card"><h2>MESAS DE 10 FICHAS</h2><p>Mesa #1022 • 2 jugadores • En vivo</p><p>Apuesta: 10 fichas</p><button class="btn" style="width:100%" onclick="entrarMesa(1022,10)">ENTRAR - JUGAR DE VERDAD</button></div>
<div class="card"><h2>MESAS DE 20 FICHAS</h2><p>Mesa #1023 • 2 jugadores • En vivo</p><p>Apuesta: 20 fichas</p><button class="btn" style="width:100%" onclick="entrarMesa(1023,20)">ENTRAR - JUGAR DE VERDAD</button></div>
</div>

<div class="wrap oculto" id="juego">
<button class="btn" onclick="salir()">← SALIR AL LOBBY</button>
<h2 id="tituloMesa">Mesa #1021</h2>
<div class="info" id="turno">Tu turno - Toca una ficha verde para jugar</div>
<div style="text-align:center">🤖 BOT - <span id="botCount">7</span> fichas</div>
<div class="mesa" id="mesa"></div>
<div class="info">Extremos: <b id="extremos">-</b> | <span id="msg">Te repartimos 7 fichas. Tú sales.</span></div>
<h3 style="text-align:center">TUS FICHAS - Toca para jugar</h3>
<div class="mano" id="mano"></div>
<div style="text-align:center;margin-top:12px"><button class="btn" id="btnPasar" onclick="pasar()" style="background:#eab308;color:#000">PASAR TURNO</button> <button class="btn" onclick="nuevaPartida()">🔄 NUEVA PARTIDA</button></div>
</div>
<div class="nav"><b>🏠 Lobby</b><b>🃏 Mis Mesas</b><b>🏆 Clasificación</b><b>🛒 Tienda</b></div>

<script>
let saldo=12450, apuesta=5, mesaId=1021;
let mazo=[], mano=[], bot=[], mesa=[], izq=null, der=null, miTurno=true, fin=false;

function crearMazo(){mazo=[];for(let a=0;a<=6;a++)for(let b=a;b<=6;b++)mazo.push([a,b]);}
function mezclar(){for(let i=mazo.length-1;i>0;i--){let j=Math.floor(Math.random()*(i+1));[mazo[i],mazo[j]]=[mazo[j],mazo[i]];}}
function fichaHTML(f,clase="",h=false){return `<div class="ficha ${clase} ${h?'h':''}"><span>${f[0]}</span><hr><span>${f[1]}</span></div>`;}
function entrarMesa(id,ap){mesaId=id;apuesta=ap;document.getElementById('lobby').classList.add('oculto');document.getElementById('juego').classList.remove('oculto');document.getElementById('tituloMesa').innerText='Mesa #'+id+' - Apuesta '+ap+' fichas';nuevaPartida();}
function salir(){document.getElementById('juego').classList.add('oculto');document.getElementById('lobby').classList.remove('oculto');}
function nuevaPartida(){crearMazo();mezclar();mano=mazo.slice(0,7);bot=mazo.slice(7,14);mesa=[];izq=null;der=null;miTurno=true;fin=false;document.getElementById('msg').innerText='Te repartimos 7 fichas. Tú sales.';render();}
function puedeJugar(f){if(mesa.length===0) return true;return f[0]===izq||f[1]===izq||f[0]===der||f[1]===der;}
function render(){
  document.getElementById('saldo').innerText=saldo;
  document.getElementById('botCount').innerText=bot.length;
  document.getElementById('extremos').innerText=mesa.length?izq+' | '+der:'-';
  document.getElementById('turno').innerText=fin?'Partida terminada':(miTurno?'✅ TU TURNO - Toca una ficha verde':'⏳ Turno del BOT...');
  let mh=document.getElementById('mesa'); mh.innerHTML=mesa.length?mesa.map((f,i)=>fichaHTML(f,'enmesa',i%2===1)).join(''):'<p style="color:#fff">Mesa vacía. Juega tu primera ficha.</p>';
  let man=document.getElementById('mano');
  man.innerHTML=mano.map((f,i)=>{let ok=miTurno&&!fin&&puedeJugar(f);return `<div onclick="jugar(${i})">${fichaHTML(f,ok?'jugable':'')}</div>`}).join('');
  document.getElementById('btnPasar').style.display=(miTurno&&!fin&&mesa.length>0&&!mano.some(puedeJugar))?'inline-block':'none';
}
function colocar(f, lado){
  if(mesa.length===0){mesa.push(f);izq=f[0];der=f[1];return;}
  if(lado==='izq'){if(f[1]===izq){mesa.unshift(f);izq=f[0];}else if(f[0]===izq){mesa.unshift([f[1],f[0]]);izq=f[1];}}
  else{if(f[0]===der){mesa.push(f);der=f[1];}else if(f[1]===der){mesa.push([f[1],f[0]]);der=f[0];}}
}
function jugar(i){
  if(!miTurno||fin) return;
  let f=mano[i];
  if(!puedeJugar(f)){document.getElementById('msg').innerText='Esa ficha no pega. Busca una que tenga '+izq+' o '+der;return;}
  mano.splice(i,1);
  if(mesa.length===0){colocar(f,'izq');}
  else if(f[0]===izq||f[1]===izq){colocar(f,'izq');}
  else{colocar(f,'der');}
  document.getElementById('msg').innerText='Jugaste ['+f[0]+'|'+f[1]+']';
  if(mano.length===0){ganar(true);return;}
  miTurno=false;render();
  setTimeout(turnoBot,900);
}
function turnoBot(){
  if(fin) return;
  let idx=bot.findIndex(puedeJugar);
  if(idx===-1){document.getElementById('msg').innerText='El BOT pasó. Te toca a ti.';miTurno=true;render();verificarTranca();return;}
  let f=bot.splice(idx,1)[0];
  if(mesa.length===0) colocar(f,'izq');
  else if(f[0]===izq||f[1]===izq) colocar(f,'izq');
  else colocar(f,'der');
  document.getElementById('msg').innerText='BOT jugó ['+f[0]+'|'+f[1]+']';
  if(bot.length===0){ganar(false);return;}
  miTurno=true;render();verificarTranca();
}
function pasar(){if(!miTurno||fin) return;miTurno=false;document.getElementById('msg').innerText='Pasaste. Turno del BOT';render();setTimeout(turnoBot,700);}
function verificarTranca(){
  if(mano.some(puedeJugar)||bot.some(puedeJugar)) return;
  let miPuntos=mano.reduce((s,f)=>s+f[0]+f[1],0);
  let botPuntos=bot.reduce((s,f)=>s+f[0]+f[1],0);
  if(miPuntos<botPuntos) ganar(true,true); else if(botPuntos<miPuntos) ganar(false,true); else {fin=true;document.getElementById('msg').innerText='EMPATE - Tranca. Nadie gana.';render();}
}
function ganar(yo,tranca=false){
  fin=true;
  if(yo){saldo+=apuesta;document.getElementById('msg').innerText=(tranca?'¡TRANCA! GANASTE por menos puntos. ':'¡GANASTE! Te quedaste sin fichas. ')+'+'+apuesta+' fichas';}
  else{saldo-=apuesta;if(saldo<0)saldo=0;document.getElementById('msg').innerText=(tranca?'TRANCA - Perdiste, el BOT tenía menos puntos. ':'PERDISTE. El BOT se quedó sin fichas. ')+'-'+apuesta+' fichas';}
  render();setTimeout(()=>alert(document.getElementById('msg').innerText+'\nSaldo: '+saldo),300);
}
try{Telegram.WebApp.ready();Telegram.WebApp.expand();}catch(e){}
</script></body></html>
"""

@app.route("/")
def index():
    return "Club de Domino - OK - Ve a /app"

@app.route("/app")
def app_page():
    return Response(HTML, mimetype="text/html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
