from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NEXUS OMEGA</title>
    <style>
        /* --- CORE THEME: DEEP CYBER --- */
        :root {
            --bg: #000000;
            --panel: #0b0b0b;
            --border: #2a2a2a;
            --primary: #00ff41; /* Hacker Green */
            --secondary: #00e5ff; /* Cyan */
            --danger: #ff003c; /* Red */
            --text: #e0e0e0;
            --chat-bg: #050505;
        }

        body { 
            background-color: var(--bg); color: var(--text); 
            font-family: 'Consolas', monospace; margin: 0; padding: 0;
            height: 100vh; display: flex; flex-direction: column; overflow: hidden;
        }

        /* --- NAVIGATION --- */
        nav { display: flex; border-bottom: 1px solid var(--border); background: #080808; height: 50px; }
        .nav-item {
            flex: 1; display: flex; align-items: center; justify-content: center;
            font-size: 12px; font-weight: bold; color: #666; cursor: pointer;
            border-right: 1px solid #1a1a1a; transition: 0.2s;
        }
        .nav-item.active { background: #111; color: var(--primary); border-bottom: 2px solid var(--primary); }
        .nav-attack.active { color: var(--danger); border-color: var(--danger); }
        .nav-spy.active { color: var(--secondary); border-color: var(--secondary); }

        /* --- LAYOUTS --- */
        .page { display: none; height: calc(100vh - 50px); overflow-y: auto; padding: 10px; }
        .page.active { display: block; }

        .box { background: var(--panel); border: 1px solid var(--border); padding: 10px; margin-bottom: 10px; border-radius: 4px; }
        .box-head { 
            font-size: 11px; font-weight: bold; color: var(--primary); 
            border-bottom: 1px dashed #333; padding-bottom: 5px; margin-bottom: 10px;
            display: flex; justify-content: space-between; 
        }

        /* --- INPUTS & BUTTONS --- */
        input, textarea, select {
            width: 100%; background: #000; border: 1px solid #444; color: #fff;
            padding: 8px; margin-top: 4px; border-radius: 2px; font-family: monospace; font-size: 11px;
            box-sizing: border-box; outline: none;
        }
        textarea { height: 60px; color: yellow; resize: vertical; }
        
        .btn-row { display: flex; gap: 5px; margin-top: 10px; }
        button {
            flex: 1; padding: 10px; font-weight: bold; cursor: pointer; border: none; 
            border-radius: 2px; font-size: 11px; color: white; text-transform: uppercase;
        }
        .btn-green { background: #005500; border: 1px solid var(--primary); }
        .btn-red { background: #550000; border: 1px solid var(--danger); }
        .btn-blue { background: #003355; border: 1px solid var(--secondary); }
        .btn-sm { padding: 3px 8px; width: auto; font-size: 9px; flex: none; }

        /* --- LISTS & CHAT --- */
        .scroll-list { height: 150px; overflow-y: auto; background: var(--chat-bg); border: 1px solid #222; padding: 5px; font-size: 11px; }
        
        /* CHAT MESSAGES */
        .msg { margin-bottom: 2px; padding: 2px; border-bottom: 1px solid #111; word-wrap: break-word; }
        .msg-time { color: #555; font-size: 9px; margin-right: 5px; }
        .msg-user { font-weight: bold; color: #aaa; margin-right: 5px; }
        .msg-text { color: #ddd; }
        .msg-bot .msg-user { color: var(--primary); } /* My Bot */
        .msg-target .msg-user { color: var(--danger); } /* Target */
        .msg-target { background: rgba(255, 0, 60, 0.1); }

        /* USER ROWS */
        .user-row { display: flex; align-items: center; justify-content: space-between; padding: 5px; border-bottom: 1px solid #1a1a1a; cursor: pointer; }
        .user-row:hover { background: #111; }
        .u-info { display: flex; align-items: center; gap: 8px; }
        .u-pic { width: 20px; height: 20px; border-radius: 50%; border: 1px solid #333; }
        
        .tag { font-size: 8px; padding: 2px 4px; border-radius: 2px; }
        .tag-bot { background: var(--primary); color: black; }
        .tag-target { background: var(--danger); color: white; animation: blink 1s infinite; }

        @keyframes blink { 50% { opacity: 0.5; } }
    </style>
</head>
<body>

<nav>
    <div class="nav-item active" onclick="tab('dash', this)">DASHBOARD</div>
    <div class="nav-item nav-attack" onclick="tab('attack', this)">WAR ROOM</div>
    <div class="nav-item nav-spy" onclick="tab('spy', this)">SURVEILLANCE</div>
</nav>

<!-- 1. DASHBOARD (CONNECTION) -->
<div id="dash" class="page active">
    <div class="box">
        <div class="box-head"><span>📡 CONNECTION CENTER</span></div>
        <label>🎯 Target Room</label>
        <input type="text" id="roomName" value="ملتقى🥂العرب">
        
        <label>📝 Bot Accounts (user#pass@...)</label>
        <textarea id="accString" placeholder="bot1#pass123@bot2#pass123@"></textarea>
        
        <div class="btn-row">
            <button class="btn-green" onclick="connectBots()">🔌 CONNECT ALL</button>
            <button class="btn-red" onclick="disconnectAll()">❌ KILL SWITCH</button>
        </div>
    </div>

    <div class="box">
        <div class="box-head"><span>🤖 CONNECTED BOTS (<span id="cntBot">0</span>)</span></div>
        <div id="botList" class="scroll-list" style="height:100px;"></div>
    </div>

    <div class="box">
        <div class="box-head"><span>📜 SYSTEM LOGS</span></div>
        <div id="sysLogs" class="scroll-list" style="height:100px; color:#888;"></div>
    </div>
</div>

<!-- 2. WAR ROOM (ATTACK) -->
<div id="attack" class="page">
    <div class="box" style="border-color: var(--danger);">
        <div class="box-head" style="color:var(--danger)">⚔️ ATTACK CONFIG</div>
        
        <div style="display:flex; gap:5px;">
            <div style="flex:1"><label>Speed (ms)</label><input type="number" id="speed" value="2000"></div>
            <div style="flex:1"><label>Burst</label><input type="number" id="burst" value="1"></div>
        </div>

        <div style="display:flex; gap:5px;">
            <div style="flex:1">
                <label>Mode</label>
                <select id="mode">
                    <option value="custom">Custom Text</option>
                    <option value="ascii">Random ASCII</option>
                </select>
            </div>
        </div>

        <label>Message</label>
        <input type="text" id="msgText" placeholder="Spam text...">

        <div class="btn-row">
            <button class="btn-red" id="btnSpam" onclick="toggleSpam()">🔥 START ATTACK</button>
        </div>
    </div>

    <!-- Live Attack Feed -->
    <div class="box">
        <div class="box-head"><span>📡 LIVE BATTLEFIELD (ROOM CHAT)</span></div>
        <div id="attackChat" class="scroll-list" style="height:200px;"></div>
    </div>
    
    <div class="box">
        <div class="box-head"><span>🔫 ACTIVE SHOOTERS (BOTS)</span></div>
        <div id="activeBotList" class="scroll-list" style="height:80px;"></div>
    </div>
</div>

<!-- 3. SURVEILLANCE (SPY) -->
<div id="spy" class="page">
    <div class="box" style="border-color: var(--secondary);">
        <div class="box-head" style="color:var(--secondary)">
            <span>👁️ MULTI-TARGET MANAGER</span>
            <span id="targetCount" style="color:white">0 Locked</span>
        </div>
        
        <div class="btn-row">
            <button class="btn-blue" id="btnCopy" onclick="toggleCopycat()">🦜 START COPYCAT</button>
            <button class="btn-red" onclick="clearTargets()">🗑️ UNLOCK ALL</button>
        </div>
    </div>

    <!-- Dual View -->
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:5px; height:250px;">
        <!-- Left: User List -->
        <div class="box" style="margin:0; display:flex; flex-direction:column;">
            <div class="box-head"><span>👥 USERS</span></div>
            <div id="userList" class="scroll-list" style="flex:1; height:auto;"></div>
        </div>
        <!-- Right: Target Chat -->
        <div class="box" style="margin:0; display:flex; flex-direction:column;">
            <div class="box-head">
                <span>🎯 TARGET LOGS</span>
                <button class="btn-sm btn-green" onclick="dlTarget()">💾</button>
            </div>
            <div id="spyChat" class="scroll-list" style="flex:1; height:auto;"></div>
        </div>
    </div>

    <!-- Full Room Chat -->
    <div class="box" style="margin-top:10px;">
        <div class="box-head">
            <span>🌍 FULL ROOM HISTORY</span>
            <button class="btn-sm btn-green" onclick="dlFull()">💾</button>
        </div>
        <div id="fullChat" class="scroll-list" style="height:150px;"></div>
    </div>
</div>

<script>
    // --- CORE VARIABLES ---
    let bots = [];
    let isConnected = false;
    let isSpamming = false;
    let isCopycat = false;
    let spamInterval = null;
    
    // Data Storage
    let usersMap = new Map();
    let myBotNames = [];
    let targetSet = new Set(); // Multi-Target
    
    // Logs Storage (Memory)
    let fullLogs = [];
    let targetLogs = [];

    // --- NAVIGATION ---
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

    // --- UI RENDERERS ---
    function renderBots() {
        let h1 = document.getElementById("botList");
        let h2 = document.getElementById("activeBotList");
        h1.innerHTML = ""; h2.innerHTML = "";
        document.getElementById("cntBot").innerText = bots.length;

        bots.forEach(b => {
            let color = b.joined ? "lime" : "red";
            let status = b.joined ? "ONLINE" : "WAIT";
            let html = `<div style="display:flex; justify-content:space-between; border-bottom:1px solid #222; padding:3px;">
                <span>${b.user}</span> <span style="color:${color}">${status}</span>
            </div>`;
            h1.innerHTML += html;
            if(b.joined) h2.innerHTML += html; // Also show in Attack tab
        });
    }

    function renderUsers() {
        let box = document.getElementById("userList");
        box.innerHTML = "";
        
        usersMap.forEach(u => {
            let name = u.name || u.username || "Unknown";
            let icon = u.avatar_url || u.icon || "https://ui-avatars.com/api/?name="+name;
            if(!icon.startsWith("http")) icon = "https://chatp.net"+icon;

            let isMe = myBotNames.includes(name);
            let isTarget = targetSet.has(name);

            let row = document.createElement("div");
            row.className = "user-row";
            row.onclick = () => toggleTarget(name);

            let tag = "";
            if(isMe) tag = `<span class="tag tag-bot">BOT</span>`;
            if(isTarget) tag = `<span class="tag tag-target">TARGET</span>`;

            row.innerHTML = `
                <div class="u-info">
                    <img src="${icon}" class="u-pic">
                    <span style="color:${isTarget ? 'var(--danger)' : (isMe?'var(--primary)':'#ccc')}">${name}</span>
                </div>
                ${tag}
            `;
            box.appendChild(row);
        });
    }

    function addChatMessage(from, msg, isMe) {
        let time = new Date().toLocaleTimeString().split(" ")[0];
        let isTarget = targetSet.has(from);
        
        let typeClass = isMe ? "msg-bot" : (isTarget ? "msg-target" : "");
        
        let html = `
            <div class="msg ${typeClass}">
                <span class="msg-time">${time}</span>
                <span class="msg-user">${from}:</span>
                <span class="msg-text">${msg}</span>
            </div>
        `;

        // Update All Windows
        let feed1 = document.getElementById("fullChat");
        let feed2 = document.getElementById("attackChat");
        
        // Use insertAdjacentHTML for performance
        feed1.insertAdjacentHTML('beforeend', html);
        feed2.insertAdjacentHTML('beforeend', html);
        
        // Auto Scroll
        feed1.scrollTop = feed1.scrollHeight;
        feed2.scrollTop = feed2.scrollHeight;

        // Save Log
        fullLogs.push(`[${time}] ${from}: ${msg}`);

        // If Target, Update Spy Window
        if(isTarget) {
            let spyBox = document.getElementById("spyChat");
            spyBox.insertAdjacentHTML('beforeend', html);
            spyBox.scrollTop = spyBox.scrollHeight;
            targetLogs.push(`[${time}] ${from}: ${msg}`);
        }
    }

    // --- SPY LOGIC ---
    function toggleTarget(name) {
        if(targetSet.has(name)) targetSet.delete(name);
        else targetSet.add(name);
        
        document.getElementById("targetCount").innerText = targetSet.size + " Locked";
        renderUsers();
    }

    function clearTargets() {
        targetSet.clear();
        renderUsers();
        document.getElementById("targetCount").innerText = "0 Locked";
    }

    function toggleCopycat() {
        isCopycat = !isCopycat;
        let btn = document.getElementById("btnCopy");
        if(isCopycat) {
            btn.innerText = "🦜 STOP COPY";
            btn.style.border = "1px solid var(--danger)";
        } else {
            btn.innerText = "🦜 START COPYCAT";
            btn.style.border = "1px solid var(--secondary)";
        }
    }

    // --- DOWNLOADS ---
    function dlFull() { download(fullLogs.join("\\n"), "full_chat.txt"); }
    function dlTarget() { download(targetLogs.join("\\n"), "target_chat.txt"); }
    
    function download(text, name) {
        let blob = new Blob([text], {type: "text/plain;charset=utf-8"});
        let a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = name;
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

                // MASTER BOT TASKS (Listeners)
                if(this.isMaster) {
                    // ROSTER
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

                    // CHAT LISTENER
                    if(data.handler === "room_event" && data.type === "text") {
                        let isMe = myBotNames.includes(data.from);
                        addChatMessage(data.from, data.body, isMe);

                        // COPYCAT TRIGGER
                        if(isCopycat && targetSet.has(data.from)) {
                            broadcast(data.body); // Repeat what target said
                        }
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
            // FIXED METHOD A PAYLOAD
            this.send({
                handler: "room_message", id: genId(), room: this.room,
                type: "text", body: txt, url: "", length: ""
            });
        }
        
        disconnect() { if(this.ws) this.ws.close(); }
    }

    // --- CONTROLLERS ---
    function broadcast(msg) {
        let burst = parseInt(document.getElementById("burst").value) || 1;
        bots.forEach(b => {
            if(b.joined) {
                for(let k=0; k<burst; k++) b.sendMessage(msg);
            }
        });
    }

    function connectBots() {
        let room = document.getElementById("roomName").value;
        let raw = document.getElementById("accString").value;
        if(!raw.includes("#")) { alert("No Bots!"); return; }

        usersMap.clear(); myBotNames = []; bots = [];
        renderUsers(); renderBots();

        let list = raw.split("@").filter(s => s.includes("#"));
        
        list.forEach((s, i) => {
            let [u, p] = s.split("#");
            let cleanU = u.trim();
            myBotNames.push(cleanU);
            
            let isMaster = (i === 0);
            let bot = new Bot(cleanU, p.trim(), room, isMaster);
            bots.push(bot);
            setTimeout(() => bot.connect(), i * 600);
        });
        
        log("System Online. Connecting...");
    }

    function toggleSpam() {
        let btn = document.getElementById("btnSpam");
        if(isSpamming) {
            // STOP
            isSpamming = false;
            clearInterval(spamInterval);
            btn.innerText = "🔥 START ATTACK";
            btn.classList.replace("btn-green", "btn-red");
        } else {
            // START
            isSpamming = true;
            let speed = parseInt(document.getElementById("speed").value);
            btn.innerText = "⏸️ STOP ATTACK";
            btn.classList.replace("btn-red", "btn-green");

            spamInterval = setInterval(() => {
                let mode = document.getElementById("mode").value;
                let txt = document.getElementById("msgText").value || ".";
                let msg = (mode === "ascii") ? ASCII[Math.floor(Math.random()*ASCII.length)] : txt;
                broadcast(msg);
            }, speed);
        }
    }

    function disconnectAll() {
        if(isSpamming) toggleSpam();
        bots.forEach(b => b.disconnect());
        bots = [];
        renderBots();
        log("All Disconnected.");
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