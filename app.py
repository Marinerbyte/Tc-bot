from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NEXUS SCROLL</title>
    <style>
        /* --- THEME --- */
        :root {
            --bg: #050505;
            --panel: #111;
            --border: #222;
            --green: #00ff41;
            --red: #ff003c;
            --blue: #00e5ff;
            --text: #ddd;
        }

        * { box-sizing: border-box; }

        body { 
            background-color: var(--bg); color: var(--text); 
            font-family: 'Courier New', monospace; margin: 0; padding: 0;
            padding-bottom: 80px; /* Scroll Space */
        }

        /* --- STICKY NAV --- */
        nav { 
            display: flex; position: sticky; top: 0; z-index: 1000;
            background: #000; border-bottom: 2px solid var(--green);
            box-shadow: 0 4px 10px rgba(0,0,0,0.8);
        }
        .nav-item {
            flex: 1; text-align: center; padding: 15px 0; font-size: 12px; 
            font-weight: bold; color: #555; cursor: pointer; border-right: 1px solid #111;
            background: #080808;
        }
        .nav-item.active { background: #001a00; color: var(--green); }
        .nav-attack.active { color: var(--red); background: #1a0000; }
        .nav-spy.active { color: var(--blue); background: #001a1a; }

        /* --- LAYOUT --- */
        .page { display: none; padding: 15px; animation: fadeIn 0.3s; }
        .page.active { display: block; }
        @keyframes fadeIn { from{opacity:0} to{opacity:1} }

        .box { 
            background: var(--panel); border: 1px solid var(--border); 
            padding: 12px; margin-bottom: 15px; border-radius: 6px;
        }
        .head { 
            font-size: 13px; font-weight: bold; color: var(--green); 
            border-bottom: 1px dashed #333; padding-bottom: 8px; margin-bottom: 10px;
            display: flex; justify-content: space-between;
        }

        /* --- FORMS --- */
        label { font-size: 11px; color: #888; display: block; margin-top: 8px; font-weight: bold; }
        input, textarea, select {
            width: 100%; background: #000; border: 1px solid #444; color: #fff;
            padding: 10px; margin-top: 4px; border-radius: 4px; font-family: monospace; font-size: 12px;
        }
        textarea { height: 80px; color: yellow; resize: vertical; }
        input:focus { border-color: var(--green); outline: none; }

        /* --- BUTTONS --- */
        .btn-row { display: flex; gap: 10px; margin-top: 15px; }
        button {
            flex: 1; padding: 12px; font-weight: bold; cursor: pointer; 
            border: none; border-radius: 4px; font-size: 12px; color: white;
            text-transform: uppercase;
        }
        .b-green { background: #006400; border: 1px solid var(--green); }
        .b-red { background: #640000; border: 1px solid var(--red); }
        .b-blue { background: #004d66; border: 1px solid var(--blue); }
        .b-sm { padding: 4px 8px; font-size: 10px; width: auto; flex: none; }

        /* --- SCROLL LISTS --- */
        .list-box {
            max-height: 250px; overflow-y: auto; background: #000; 
            border: 1px solid #333; padding: 5px; font-size: 11px;
        }
        
        .row-item { 
            display: flex; justify-content: space-between; align-items: center;
            padding: 6px; border-bottom: 1px solid #1a1a1a; 
        }
        
        .u-pic { width: 28px; height: 28px; border-radius: 50%; border: 1px solid #444; margin-right: 10px; }
        
        /* TAGS */
        .tag { font-size: 9px; padding: 2px 5px; border-radius: 3px; font-weight: bold; }
        .t-on { color: lime; border: 1px solid lime; }
        .t-off { color: red; border: 1px solid red; }
        .t-tgt { background: var(--red); color: white; animation: blink 1s infinite; }

        /* CHAT */
        .msg { margin-bottom: 5px; padding: 3px; border-bottom: 1px solid #111; word-wrap: break-word; }
        .msg-usr { font-weight: bold; color: #aaa; margin-right: 5px; }
        .msg-me .msg-usr { color: var(--green); }
        .msg-tgt { background: rgba(255, 0, 60, 0.15); border-left: 3px solid var(--red); }

        @keyframes blink { 50% { opacity: 0.5; } }
    </style>
</head>
<body>

<!-- NAVIGATION -->
<nav>
    <div class="nav-item active" onclick="tab('dash', this)">DASHBOARD</div>
    <div class="nav-item nav-attack" onclick="tab('attack', this)">ATTACK</div>
    <div class="nav-item nav-spy" onclick="tab('spy', this)">SPY</div>
</nav>

<!-- 1. DASHBOARD -->
<div id="dash" class="page active">
    <div class="box">
        <div class="head"><span>📡 SETUP CONNECTION</span></div>
        
        <label>TARGET ROOM</label>
        <input type="text" id="room" value="ملتقى🥂العرب">
        
        <label>ACCOUNTS (user#pass@...)</label>
        <textarea id="accs" placeholder="bot1#pass123@bot2#pass123@"></textarea>
        
        <div class="btn-row">
            <button class="b-green" onclick="connect()">🔌 CONNECT</button>
            <button class="b-red" onclick="kill()">❌ KILL ALL</button>
        </div>
    </div>

    <div class="box">
        <div class="head"><span>🤖 ACTIVE BOTS: <span id="cntBot">0</span></span></div>
        <div id="botList" class="list-box"></div>
    </div>

    <div class="box">
        <div class="head"><span>📜 SYSTEM LOGS</span></div>
        <div id="sysLogs" class="list-box" style="color:#888;"></div>
    </div>
</div>

<!-- 2. ATTACK -->
<div id="attack" class="page">
    <div class="box" style="border-color: var(--red);">
        <div class="head" style="color:var(--red)">⚔️ ATTACK CONFIG</div>
        
        <div style="display:flex; gap:10px;">
            <div style="flex:1"><label>SPEED (ms)</label><input type="number" id="speed" value="2000"></div>
            <div style="flex:1"><label>BURST</label><input type="number" id="burst" value="1"></div>
        </div>

        <div style="display:flex; gap:10px;">
            <div style="flex:1">
                <label>MODE</label>
                <select id="mode">
                    <option value="custom">Custom Text</option>
                    <option value="ascii">Random ASCII</option>
                </select>
            </div>
        </div>
        
        <label>MESSAGE</label>
        <input type="text" id="msg" placeholder="Spam text...">

        <div class="btn-row">
            <button class="b-red" id="btnSpam" onclick="toggleSpam()">🔥 START FIRE</button>
            <button class="b-blue" onclick="testFire()">🔫 TEST 1 MSG</button>
        </div>
    </div>

    <div class="box">
        <div class="head"><span>📡 LIVE ROOM CHAT</span></div>
        <div id="attackFeed" class="list-box" style="height:300px;"></div>
    </div>
</div>

<!-- 3. SPY -->
<div id="spy" class="page">
    <div class="box" style="border-color: var(--blue);">
        <div class="head" style="color:var(--blue)">
            <span>👁️ TARGET LIST</span>
            <span id="tgtCount" style="color:white">0 Locked</span>
        </div>
        <div style="text-align:center; font-size:10px; color:#666; margin-bottom:10px;">Tap users below to lock target</div>
        
        <div class="btn-row">
            <button class="b-blue" id="btnCopy" onclick="toggleCopy()">🦜 COPYCAT: OFF</button>
            <button class="b-green" onclick="dlChat()">💾 SAVE</button>
        </div>
        <button class="b-red" style="width:100%; margin-top:10px;" onclick="clearTgt()">UNLOCK ALL</button>
    </div>

    <div class="box">
        <div class="head"><span>👥 ROOM USERS (<span id="usrCount">0</span>)</span></div>
        <div id="userList" class="list-box" style="height:300px;"></div>
    </div>

    <div class="box">
        <div class="head"><span>🎯 TARGET LOGS</span></div>
        <div id="spyFeed" class="list-box" style="height:200px;"></div>
    </div>
</div>

<script>
    // --- VARIABLES ---
    let bots = [], users = new Map(), targets = new Set(), myNames = [];
    let isCon = false, isSpam = false, isCopy = false, spamInt = null;
    let logs = [];

    // --- UTILS ---
    function tab(id, btn) {
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        document.getElementById(id).classList.add('active');
        btn.classList.add('active');
    }

    function log(msg) {
        let d = document.createElement("div");
        d.innerText = "> " + msg;
        document.getElementById("sysLogs").prepend(d);
    }

    function genId(len=20) {
        let c="abcdef0123456789",s="";
        for(let i=0;i<len;i++) s+=c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    // --- UI RENDER ---
    function renderBots() {
        let box = document.getElementById("botList");
        box.innerHTML = "";
        document.getElementById("cntBot").innerText = bots.length;
        bots.forEach(b => {
            let cls = b.joined ? "t-on" : "t-off";
            let txt = b.joined ? "ONLINE" : "WAIT";
            box.innerHTML += `<div class="row-item"><span>${b.user}</span><span class="tag ${cls}">${txt}</span></div>`;
        });
    }

    function renderUsers() {
        let box = document.getElementById("userList");
        box.innerHTML = "";
        document.getElementById("usrCount").innerText = users.size;

        users.forEach(u => {
            let name = u.name || u.username || "Unknown";
            let icon = u.avatar_url || u.icon || "https://ui-avatars.com/api/?name="+name;
            if(!icon.startsWith("http")) icon = "https://chatp.net"+icon;

            let isMe = myNames.includes(name);
            let isTgt = targets.has(name);
            let tag = "";
            if(isMe) tag = `<span class="tag" style="border:1px solid lime; color:lime;">BOT</span>`;
            if(isTgt) tag = `<span class="tag t-tgt">TARGET</span>`;

            let row = document.createElement("div");
            row.className = "row-item";
            row.style.cursor = "pointer";
            row.onclick = () => toggleTgt(name);
            
            row.innerHTML = `
                <div style="display:flex; align-items:center;">
                    <img src="${icon}" class="u-pic">
                    <span style="color:${isTgt?'var(--red)':'#ccc'}">${name}</span>
                </div>
                ${tag}
            `;
            box.appendChild(row);
        });
    }

    function addChat(from, msg) {
        let time = new Date().toLocaleTimeString().split(" ")[0];
        let isMe = myNames.includes(from);
        let isTgt = targets.has(from);
        let cls = isMe ? "msg-me" : (isTgt ? "msg-tgt" : "");

        let html = `
            <div class="msg ${cls}">
                <span class="msg-time">[${time}]</span>
                <span class="msg-usr">${from}:</span>
                <span>${msg}</span>
            </div>
        `;

        let feed = document.getElementById("attackFeed");
        feed.insertAdjacentHTML('beforeend', html);
        feed.scrollTop = feed.scrollHeight;

        if(isTgt) {
            let sf = document.getElementById("spyFeed");
            sf.insertAdjacentHTML('beforeend', html);
            sf.scrollTop = sf.scrollHeight;
            logs.push(`[${time}] ${from}: ${msg}`);
            if(isCopy && isCon) broadcast(msg);
        }
    }

    // --- SPY LOGIC ---
    function toggleTgt(name) {
        if(targets.has(name)) targets.delete(name);
        else targets.add(name);
        document.getElementById("tgtCount").innerText = targets.size + " Locked";
        renderUsers();
    }
    function clearTgt() { targets.clear(); renderUsers(); }
    
    function toggleCopy() {
        isCopy = !isCopy;
        let btn = document.getElementById("btnCopy");
        btn.innerText = isCopy ? "🦜 COPY: ON" : "🦜 COPY: OFF";
        btn.className = isCopy ? "b-red" : "b-blue";
    }

    function dlChat() {
        if(logs.length===0) return;
        let blob = new Blob([logs.join("\\n")], {type: "text/plain"});
        let a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "spy.txt";
        a.click();
    }

    // --- BOT ENGINE ---
    const ASCII = ["(｡♥‿♥｡)", "ʕ•ᴥ•ʔ", "🔥", "❤️", "⚡", "🚀", "💀"];

    class Bot {
        constructor(user, pass, room, isMaster) {
            this.user = user; this.pass = pass; this.room = room; 
            this.ws = null; this.joined = false; this.isMaster = isMaster;
        }

        connect() {
            if(this.ws) return;
            this.ws = new WebSocket("wss://chatp.net:5333/server");

            this.ws.onopen = () => {
                this.send({ handler: "login", id: genId(), username: this.user, password: this.pass });
            };

            this.ws.onmessage = (e) => {
                let data = JSON.parse(e.data);

                if(data.handler === "login_event" && data.type === "success") {
                    this.send({ handler: "room_join", id: genId(), name: this.room });
                }
                
                else if(data.handler === "room_event" && data.type === "you_joined") {
                    this.joined = true;
                    renderBots();
                    if(this.isMaster && data.users) {
                        data.users.forEach(u => users.set(u.username, u));
                        renderUsers();
                    }
                }
                
                else if(data.handler === "room_event" && data.type === "room_joined") {
                    this.joined = true; renderBots();
                }

                if(this.isMaster) {
                    if((data.handler === "roster" || data.handler === "room_users") && data.users) {
                        data.users.forEach(u => users.set(u.username, u));
                        renderUsers();
                    }
                    if(data.handler === "room_event" && data.type === "join") {
                        users.set(data.username, data); renderUsers();
                    }
                    if(data.handler === "room_event" && data.type === "leave") {
                        users.delete(data.username); renderUsers();
                    }
                    if(data.handler === "room_event" && data.type === "text") {
                        addChat(data.from, data.body);
                    }
                }
            };

            this.ws.onclose = () => { this.joined = false; renderBots(); };
        }

        send(json) { if(this.ws && this.ws.readyState === 1) this.ws.send(JSON.stringify(json)); }

        sendMessage(txt) {
            if(!this.joined) return;
            this.send({
                handler: "room_message", id: genId(), room: this.room,
                type: "text", body: txt, url: "", length: ""
            });
        }
        disconnect() { if(this.ws) this.ws.close(); }
    }

    // --- CONTROLLER ---
    function connect() {
        if(isCon) return;
        let room = document.getElementById("room").value;
        let raw = document.getElementById("accs").value;
        if(!raw.includes("#")) { alert("Enter Bots!"); return; }

        users.clear(); myNames=[]; bots=[]; targets.clear();
        let list = raw.split("@").filter(s => s.includes("#"));
        
        list.forEach((s, i) => {
            let [u, p] = s.split("#");
            let cln = u.trim();
            myNames.push(cln);
            let bot = new Bot(cln, p.trim(), room, (i===0));
            bots.push(bot);
            setTimeout(() => bot.connect(), i*600);
        });
        isCon = true;
        log("Connecting...");
    }

    function broadcast(txt) {
        let burst = parseInt(document.getElementById("burst").value) || 1;
        bots.forEach(b => {
            if(b.joined) { for(let k=0; k<burst; k++) b.sendMessage(txt); }
        });
    }

    function testFire() {
        let txt = document.getElementById("msg").value || "Test";
        broadcast(txt);
    }

    function toggleSpam() {
        let btn = document.getElementById("btnSpam");
        if(isSpam) {
            isSpam = false; clearInterval(spamInt);
            btn.innerText = "🔥 START FIRE"; btn.className = "b-red";
        } else {
            isSpam = true;
            btn.innerText = "⏸️ STOP"; btn.className = "b-green";
            let speed = parseInt(document.getElementById("speed").value);
            
            spamInt = setInterval(() => {
                let mode = document.getElementById("mode").value;
                let txt = document.getElementById("msg").value || ".";
                if(mode==="ascii") txt = ASCII[Math.floor(Math.random()*ASCII.length)];
                broadcast(txt);
            }, speed);
        }
    }

    function kill() {
        if(isSpam) toggleSpam();
        bots.forEach(b => b.disconnect());
        bots = []; isCon = false;
        renderBots();
        log("Disconnected.");
    }

</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CODE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)