from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NEXUS INFINITY</title>
    <style>
        /* --- THEME --- */
        :root {
            --bg: #000000;
            --card: #111111;
            --border: #222;
            --green: #00ff41;
            --red: #ff003c;
            --blue: #00ccff;
            --text: #ffffff;
        }

        body { 
            background-color: var(--bg); color: var(--text); 
            font-family: monospace; margin: 0; padding: 0;
            padding-bottom: 80px; /* Space for scrolling */
        }

        /* --- NAVIGATION (FIXED TOP) --- */
        .navbar {
            position: sticky; top: 0; z-index: 1000;
            display: flex; background: #080808; border-bottom: 2px solid var(--green);
            box-shadow: 0 5px 15px rgba(0,0,0,0.8);
        }
        .nav-btn {
            flex: 1; padding: 15px 5px; text-align: center; cursor: pointer;
            font-size: 11px; font-weight: bold; border-right: 1px solid #222;
            background: #080808; color: #666;
        }
        .nav-btn.active { color: var(--green); background: #001a00; }

        /* --- CONTAINERS --- */
        .tab { display: none; padding: 10px; }
        .tab.active { display: block; animation: fade 0.3s; }
        @keyframes fade { from {opacity:0} to {opacity:1} }

        .card {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 5px; padding: 12px; margin-bottom: 15px;
        }
        .card-head {
            font-size: 13px; font-weight: bold; border-bottom: 1px dashed #333;
            padding-bottom: 8px; margin-bottom: 10px; color: var(--green);
            display: flex; justify-content: space-between;
        }

        /* --- INPUTS --- */
        label { font-size: 10px; color: #888; display: block; margin-top: 10px; }
        input, textarea, select {
            width: 100%; background: #000; border: 1px solid #444; color: white;
            padding: 10px; margin-top: 5px; border-radius: 4px; box-sizing: border-box;
            font-family: monospace;
        }
        textarea { height: 80px; color: yellow; }
        input:focus, textarea:focus { border-color: var(--green); outline: none; }

        /* --- BUTTONS --- */
        .btn-row { display: flex; gap: 8px; margin-top: 15px; }
        button {
            flex: 1; padding: 14px; font-weight: bold; font-size: 12px;
            border: none; border-radius: 4px; cursor: pointer; color: white;
            text-transform: uppercase;
        }
        .btn-g { background: #006400; border: 1px solid var(--green); }
        .btn-r { background: #640000; border: 1px solid var(--red); }
        .btn-b { background: #004466; border: 1px solid var(--blue); }
        .btn-sm { padding: 5px 10px; font-size: 10px; width: auto; flex: none; margin: 0; }

        /* --- CHAT & LISTS --- */
        .scroll-box {
            height: 250px; overflow-y: auto; background: #000; border: 1px solid #333;
            padding: 8px; font-size: 11px;
        }
        
        .msg { margin-bottom: 6px; border-bottom: 1px solid #111; padding-bottom: 2px; }
        .msg-time { color: #555; font-size: 9px; margin-right: 5px; }
        .msg-usr { font-weight: bold; color: #aaa; }
        .msg-txt { color: #eee; word-break: break-all; }
        
        /* Highlight My Attack Messages */
        .my-attack { border-left: 3px solid var(--green); padding-left: 5px; }
        .my-attack .msg-usr { color: var(--green); }

        /* USER LIST */
        .user-row {
            display: flex; align-items: center; justify-content: space-between;
            padding: 8px; border-bottom: 1px solid #222;
        }
        .u-pic { width: 30px; height: 30px; border-radius: 50%; border: 1px solid #444; margin-right: 10px; }
        .tag { font-size: 9px; padding: 2px 5px; border-radius: 3px; }
        .tag-t { background: var(--red); color: white; animation: blink 1s infinite; }
        .tag-b { background: var(--green); color: black; }

        @keyframes blink { 50% { opacity: 0.5; } }
    </style>
</head>
<body>

<!-- TOP NAV -->
<div class="navbar">
    <div class="nav-btn active" onclick="tab('home', this)">1. CONNECT</div>
    <div class="nav-btn" onclick="tab('attack', this)">2. ATTACK</div>
    <div class="nav-btn" onclick="tab('spy', this)">3. SPY</div>
</div>

<!-- PAGE 1: CONNECT -->
<div id="home" class="tab active">
    <div class="card">
        <div class="card-head"><span>📡 SETUP</span></div>
        
        <label>TARGET ROOM</label>
        <input type="text" id="roomName" value="ملتقى🥂العرب">

        <label>BOT ACCOUNTS (user#pass@...)</label>
        <textarea id="accString" placeholder="bot1#pass123@bot2#pass123@"></textarea>

        <div class="btn-row">
            <button class="btn-g" onclick="connectAll()">🔌 CONNECT</button>
            <button class="btn-r" onclick="killAll()">❌ DISCONNECT</button>
        </div>
    </div>

    <div class="card">
        <div class="card-head">
            <span>🤖 BOTS STATUS (<span id="botCount">0</span>)</span>
        </div>
        <div id="botList" class="scroll-box" style="height: 150px;"></div>
    </div>
</div>

<!-- PAGE 2: ATTACK -->
<div id="attack" class="tab">
    <div class="card" style="border-color: var(--red);">
        <div class="card-head" style="color:var(--red)">⚔️ WAR ROOM</div>
        
        <div style="display:flex; gap:10px;">
            <div style="flex:1"><label>SPEED (ms)</label><input type="number" id="speed" value="2000"></div>
            <div style="flex:1"><label>BURST</label><input type="number" id="burst" value="1"></div>
        </div>

        <label>MESSAGE</label>
        <div style="display:flex; gap:5px;">
            <select id="mode" style="width:30%;">
                <option value="custom">Text</option>
                <option value="ascii">ASCII</option>
            </select>
            <input type="text" id="msg" placeholder="Spam text..." style="margin-top:0;">
        </div>

        <div class="btn-row">
            <button class="btn-r" id="btnSpam" onclick="toggleSpam()">🔥 AUTO FIRE</button>
            <button class="btn-b" onclick="manualFire()">🔫 TEST FIRE (1 SHOT)</button>
        </div>
    </div>

    <div class="card">
        <div class="card-head"><span>📡 LIVE BATTLEFIELD</span></div>
        <div id="attackFeed" class="scroll-box" style="height:300px;"></div>
    </div>
</div>

<!-- PAGE 3: SPY -->
<div id="spy" class="tab">
    <div class="card" style="border-color: var(--blue);">
        <div class="card-head" style="color:var(--blue)">
            <span>👁️ TARGET LIST</span>
            <button class="btn-sm btn-r" onclick="clearTargets()">UNLOCK ALL</button>
        </div>
        <div style="text-align:center; font-size:11px; margin-bottom:5px; color:#aaa;">Tap user below to lock/unlock target</div>
        
        <div class="btn-row">
            <button class="btn-b" id="btnCopy" onclick="toggleCopy()">🦜 COPYCAT: OFF</button>
            <button class="btn-g" onclick="dlChat()">💾 DOWNLOAD</button>
        </div>
    </div>

    <!-- User List -->
    <div class="card">
        <div class="card-head">
            <span>👥 ROOM USERS (<span id="uCount">0</span>)</span>
        </div>
        <div id="userList" class="scroll-box" style="height:300px;"></div>
    </div>
    
    <!-- Target Chat -->
    <div class="card">
        <div class="card-head"><span>🎯 TARGET LOGS</span></div>
        <div id="targetLog" class="scroll-box" style="height:200px;"></div>
    </div>
</div>

<script>
    // --- VARIABLES ---
    let bots = [];
    let isConnected = false;
    let isSpamming = false;
    let isCopycat = false;
    let spamInterval = null;
    let usersMap = new Map();
    let myBotNames = [];
    let targetSet = new Set();
    let fullLogs = [];
    let targetLogs = [];

    // --- NAVIGATION ---
    function tab(id, btn) {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(id).classList.add('active');
        btn.classList.add('active');
    }

    function genId(len=20) {
        let c="abcdef0123456789", s="";
        for(let i=0; i<len; i++) s += c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    // --- UI UPDATES ---
    function renderBots() {
        let box = document.getElementById("botList");
        box.innerHTML = "";
        document.getElementById("botCount").innerText = bots.length;
        bots.forEach(b => {
            let color = b.joined ? "lime" : "red";
            let st = b.joined ? "ONLINE" : "WAITING";
            box.innerHTML += `<div style="padding:5px; border-bottom:1px solid #222; display:flex; justify-content:space-between;">
                <span>${b.user}</span> <span style="color:${color}">${st}</span>
            </div>`;
        });
    }

    function renderUsers() {
        let box = document.getElementById("userList");
        box.innerHTML = "";
        document.getElementById("uCount").innerText = usersMap.size;

        usersMap.forEach(u => {
            let name = u.name || u.username || "Unknown";
            let icon = u.avatar_url || u.icon || "https://ui-avatars.com/api/?name="+name;
            if(!icon.startsWith("http")) icon = "https://chatp.net"+icon;

            let isMe = myBotNames.includes(name);
            let isTarget = targetSet.has(name);
            let tag = "";
            if(isMe) tag = `<span class="tag tag-b">BOT</span>`;
            if(isTarget) tag = `<span class="tag tag-t">TARGET</span>`;

            let row = document.createElement("div");
            row.className = "user-row";
            row.onclick = () => toggleTarget(name);
            row.innerHTML = `
                <div style="display:flex; align-items:center;">
                    <img src="${icon}" class="u-pic">
                    <span style="color:${isTarget?'var(--red)':'#ddd'}">${name}</span>
                </div>
                ${tag}
            `;
            box.appendChild(row);
        });
    }

    function addChat(from, msg) {
        let time = new Date().toLocaleTimeString().split(" ")[0];
        let isMe = myBotNames.includes(from);
        let isTarget = targetSet.has(from);
        let cls = isMe ? "my-attack" : "";

        let html = `
            <div class="msg ${cls}">
                <span class="msg-time">${time}</span>
                <span class="msg-usr" style="color:${isMe?'var(--green)':(isTarget?'var(--red)':'#aaa')}">${from}:</span>
                <span class="msg-txt">${msg}</span>
            </div>
        `;

        // Update Feeds
        let feed = document.getElementById("attackFeed");
        feed.insertAdjacentHTML('beforeend', html);
        feed.scrollTop = feed.scrollHeight;

        // Log Target
        if(isTarget) {
            let tBox = document.getElementById("targetLog");
            tBox.insertAdjacentHTML('beforeend', html);
            targetLogs.push(`[${time}] ${from}: ${msg}`);
            
            // Copycat Trigger
            if(isCopycat && isConnected) {
                broadcast(msg);
            }
        }
        
        fullLogs.push(`[${time}] ${from}: ${msg}`);
    }

    // --- SPY LOGIC ---
    function toggleTarget(name) {
        if(targetSet.has(name)) targetSet.delete(name);
        else targetSet.add(name);
        renderUsers();
    }
    
    function clearTargets() { targetSet.clear(); renderUsers(); }

    function toggleCopy() {
        isCopycat = !isCopycat;
        let btn = document.getElementById("btnCopy");
        btn.innerText = isCopycat ? "🦜 COPYCAT: ON" : "🦜 COPYCAT: OFF";
        btn.style.borderColor = isCopycat ? "var(--red)" : "var(--blue)";
    }

    function dlChat() {
        let blob = new Blob([targetLogs.join("\\n")], {type: "text/plain;charset=utf-8"});
        let a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "spy_log.txt";
        a.click();
    }

    // --- BOT ENGINE ---
    const ASCII = ["(｡♥‿♥｡)", "ʕ•ᴥ•ʔ", "🔥", "❤️", "⚡", "🚀", "💀"];

    class Bot {
        constructor(user, pass, room, isMaster) {
            this.user = user;
            this.pass = pass;
            this.room = room;
            this.ws = null;
            this.joined = false;
            this.isMaster = isMaster;
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
                else if(data.handler === "room_event" && data.type === "room_joined") {
                    this.joined = true;
                    renderBots();
                }

                // MASTER LISTENER
                if(this.isMaster) {
                    if((data.handler === "roster" || data.handler === "room_users") && data.users) {
                        data.users.forEach(u => usersMap.set(u.username, u));
                        renderUsers();
                    }
                    if(data.handler === "room_event" && data.type === "you_joined" && data.users) {
                        data.users.forEach(u => usersMap.set(u.username, u));
                        renderUsers();
                    }
                    if(data.handler === "room_event" && data.type === "join") {
                        usersMap.set(data.username, data); renderUsers();
                    }
                    if(data.handler === "room_event" && data.type === "leave") {
                        usersMap.delete(data.username); renderUsers();
                    }
                    if(data.handler === "room_event" && data.type === "text") {
                        addChat(data.from, data.body);
                    }
                }
            };

            this.ws.onclose = () => { this.joined = false; renderBots(); };
        }

        send(json) {
            if(this.ws && this.ws.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(json));
        }

        sendMessage(txt) {
            if(!this.joined) return;
            // FIXED PAYLOAD
            this.send({
                handler: "room_message", id: genId(), room: this.room,
                type: "text", body: txt, url: "", length: ""
            });
        }
        
        disconnect() { if(this.ws) this.ws.close(); }
    }

    // --- ACTIONS ---
    function connectAll() {
        if(isConnected) return;
        let room = document.getElementById("roomName").value;
        let raw = document.getElementById("accString").value;
        if(!raw.includes("#")) { alert("No Bots!"); return; }

        usersMap.clear(); myBotNames = []; bots = [];
        let list = raw.split("@").filter(s => s.includes("#"));
        
        list.forEach((s, i) => {
            let [u, p] = s.split("#");
            let cleanU = u.trim();
            myBotNames.push(cleanU);
            let bot = new Bot(cleanU, p.trim(), room, (i===0));
            bots.push(bot);
            setTimeout(() => bot.connect(), i * 600);
        });
        isConnected = true;
    }

    function broadcast(txt) {
        let burst = parseInt(document.getElementById("burst").value) || 1;
        bots.forEach(b => {
            if(b.joined) {
                for(let k=0; k<burst; k++) b.sendMessage(txt);
            }
        });
    }

    function manualFire() {
        let txt = document.getElementById("msg").value || "Test";
        let mode = document.getElementById("mode").value;
        if(mode === "ascii") txt = ASCII[Math.floor(Math.random()*ASCII.length)];
        broadcast(txt);
    }

    function toggleSpam() {
        let btn = document.getElementById("btnSpam");
        if(isSpamming) {
            isSpamming = false;
            clearInterval(spamInterval);
            btn.innerText = "🔥 AUTO FIRE";
            btn.className = "btn-r";
        } else {
            isSpamming = true;
            btn.innerText = "⏸️ STOP";
            btn.className = "btn-g";
            let speed = parseInt(document.getElementById("speed").value);
            
            spamInterval = setInterval(() => {
                let txt = document.getElementById("msg").value || ".";
                let mode = document.getElementById("mode").value;
                if(mode === "ascii") txt = ASCII[Math.floor(Math.random()*ASCII.length)];
                broadcast(txt);
            }, speed);
        }
    }

    function killAll() {
        if(isSpamming) toggleSpam();
        bots.forEach(b => b.disconnect());
        bots = [];
        isConnected = false;
        renderBots();
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