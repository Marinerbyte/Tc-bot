from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NEXUS MOBILE PRIME</title>
    <style>
        /* --- CORE THEME --- */
        :root {
            --bg: #000000;
            --panel: #0a0a0a;
            --border: #1f1f1f;
            --primary: #00ff41;
            --danger: #ff003c;
            --text-main: #e0e0e0;
            --text-dim: #666;
        }

        body { 
            background-color: var(--bg); 
            color: var(--text-main); 
            font-family: 'Courier New', monospace; 
            margin: 0; padding: 10px;
            padding-bottom: 50px; /* Space for scrolling */
        }

        /* SCROLLBARS */
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 2px; }
        ::-webkit-scrollbar-track { background: #111; }

        /* HEADER */
        .header {
            text-align: center; border-bottom: 1px solid var(--primary);
            padding-bottom: 10px; margin-bottom: 15px;
            text-transform: uppercase; letter-spacing: 2px;
            text-shadow: 0 0 10px var(--primary);
        }

        /* CARD CONTAINER */
        .card {
            background: var(--panel); border: 1px solid var(--border);
            border-radius: 6px; padding: 12px; margin-bottom: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }
        .card-title {
            color: var(--primary); font-size: 12px; font-weight: bold;
            border-bottom: 1px dashed var(--border); padding-bottom: 5px; margin-bottom: 10px;
            display: flex; justify-content: space-between;
        }

        /* INPUTS */
        label { font-size: 10px; color: var(--text-dim); display: block; margin-top: 8px; font-weight: bold; }
        input, textarea, select {
            width: 100%; background: #111; border: 1px solid #333; color: white;
            padding: 10px; margin-top: 4px; border-radius: 4px; font-family: monospace; font-size: 12px;
            box-sizing: border-box; outline: none;
        }
        input:focus, textarea:focus { border-color: var(--primary); }
        textarea { height: 70px; resize: vertical; color: yellow; }

        /* GRID LAYOUTS */
        .row { display: flex; gap: 10px; }
        .col { flex: 1; }

        /* BUTTONS */
        .btn-group { display: flex; gap: 8px; margin-top: 15px; }
        button {
            flex: 1; padding: 12px; border: none; border-radius: 4px;
            font-weight: bold; font-size: 11px; cursor: pointer; text-transform: uppercase;
            color: white; transition: 0.2s;
        }
        button:active { transform: scale(0.95); }
        .btn-green { background: #006400; border: 1px solid var(--primary); }
        .btn-red { background: #500000; border: 1px solid var(--danger); }
        .btn-blue { background: #003366; border: 1px solid #00aaff; }
        
        .btn-sm { padding: 4px 8px; font-size: 9px; width: auto; flex: none; }

        /* LISTS (SCROLLABLE AREAS) */
        .list-box {
            height: 150px; overflow-y: auto; background: #050505; 
            border: 1px solid #222; padding: 5px; margin-top: 5px;
        }
        
        /* USER ROWS */
        .user-row {
            display: flex; align-items: center; justify-content: space-between;
            padding: 6px; border-bottom: 1px solid #1a1a1a; cursor: pointer;
        }
        .user-row:active { background: #111; }
        
        .u-left { display: flex; align-items: center; gap: 8px; }
        .u-pic { width: 26px; height: 26px; border-radius: 50%; border: 1px solid #444; }
        .u-name { font-size: 12px; color: #ddd; }
        
        /* TAGS */
        .tag { font-size: 9px; padding: 2px 4px; border-radius: 3px; font-weight: bold; }
        .tag-bot { background: var(--primary); color: black; }
        .tag-target { background: var(--danger); color: white; animation: blink 1s infinite; }

        /* LOGS */
        .log-entry { font-size: 10px; margin-bottom: 2px; padding-left: 5px; border-left: 2px solid #333; word-wrap: break-word; }
        .log-sys { color: #777; }
        .log-chat { color: cyan; border-left-color: cyan; }

        @keyframes blink { 50% { opacity: 0.5; } }
    </style>
</head>
<body>

<div class="header">
    NEXUS PRIME
    <div style="font-size: 9px; color: #666; margin-top: 2px;">MOBILE COMMAND UNIT</div>
</div>

<!-- 1. CONFIGURATION -->
<div class="card">
    <div class="card-title">
        <span>📡 CONNECTION SETUP</span>
        <button class="btn-sm btn-red" onclick="document.getElementById('accString').value=''">CLR</button>
    </div>
    
    <label>🎯 TARGET ROOM</label>
    <input type="text" id="roomName" value="ملتقى🥂العرب">

    <label>📝 BOT ACCOUNTS (user#pass@...)</label>
    <textarea id="accString" placeholder="bot1#pass123@bot2#pass123@"></textarea>

    <button class="btn-blue" style="width:100%; margin-top:10px;" onclick="connectArmy()">🔌 CONNECT ALL BOTS</button>
</div>

<!-- 2. ATTACK CONTROLS -->
<div class="card">
    <div class="card-title">⚔️ ATTACK MODULE</div>

    <div class="row">
        <div class="col">
            <label>⚡ SPEED (ms)</label>
            <input type="number" id="spamSpeed" value="2000">
        </div>
        <div class="col">
            <label>💥 BURST</label>
            <input type="number" id="burstCount" value="1">
        </div>
    </div>

    <div class="row">
        <div class="col">
            <label>🎭 MODE</label>
            <select id="msgMode" onchange="toggleCopycat()">
                <option value="custom">✍️ Custom</option>
                <option value="ascii">🎲 ASCII</option>
                <option value="copycat">🦜 Copycat</option>
            </select>
        </div>
        <div class="col">
            <label>🎯 TARGET</label>
            <input type="text" id="targetUser" placeholder="Select from list..." disabled style="border-color: #333;">
        </div>
    </div>

    <label>💬 MESSAGE</label>
    <input type="text" id="customMsg" placeholder="Type here...">

    <div class="btn-group">
        <button class="btn-green" onclick="startAttack()">🔥 START</button>
        <button class="btn-red" onclick="stopAttack()">⏸️ STOP</button>
    </div>
    <button class="btn-red" style="width:100%; margin-top:10px; background:#222;" onclick="disconnectAll()">❌ DISCONNECT ALL</button>
</div>

<!-- 3. MONITORING -->
<div class="card">
    <div class="card-title">
        <span>👥 ROOM USERS (<span id="uCount">0</span>)</span>
        <span style="font-size:9px; color:#666;">(Tap to Target)</span>
    </div>
    <div id="userList" class="list-box"></div>
</div>

<!-- 4. BOT STATUS & LOGS -->
<div class="card">
    <div class="card-title">
        <span>🤖 MY BOTS (<span id="botCount">0</span>)</span>
        <button class="btn-sm btn-blue" onclick="downloadChat()">💾 LOGS</button>
    </div>
    <div id="botList" class="list-box" style="height: 100px; margin-bottom: 10px;"></div>
    
    <label>📜 LIVE TERMINAL</label>
    <div id="logs" class="list-box"></div>
</div>

<script>
    // --- VARIABLES ---
    let bots = [];
    let isConnected = false;
    let isSpamming = false;
    let spamInterval = null;
    
    let usersMap = new Map();
    let myBotNames = [];
    let chatLogs = [];

    // --- UTILS ---
    function log(msg, type="log-sys") {
        let box = document.getElementById("logs");
        let d = document.createElement("div");
        d.className = "log-entry " + type;
        d.innerText = `> ${msg}`;
        box.prepend(d);
        
        // Save for export
        if(type === "log-chat") chatLogs.push(msg);
    }

    function genId(len=20) {
        let c="abcdef0123456789", s="";
        for(let i=0; i<len; i++) s += c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    function toggleCopycat() {
        let mode = document.getElementById("msgMode").value;
        let tInput = document.getElementById("targetUser");
        if(mode === "copycat") {
            tInput.style.borderColor = "var(--danger)";
            tInput.style.color = "var(--danger)";
        } else {
            tInput.style.borderColor = "#333";
            tInput.style.color = "#aaa";
        }
        renderUsers();
    }

    // --- UI RENDERERS ---
    
    function selectTarget(name) {
        document.getElementById("targetUser").value = name;
        document.getElementById("msgMode").value = "copycat";
        toggleCopycat();
        log(`🎯 Target Locked: ${name}`, "log-sys");
        renderUsers();
    }

    function renderUsers() {
        let box = document.getElementById("userList");
        box.innerHTML = "";
        document.getElementById("uCount").innerText = usersMap.size;
        
        let target = document.getElementById("targetUser").value;

        usersMap.forEach((u) => {
            let name = u.name || u.username || "Unknown";
            let isMe = myBotNames.includes(name);
            let isTarget = (name === target);

            let icon = u.avatar_url || u.icon || "https://ui-avatars.com/api/?name="+name;
            if(icon && !icon.startsWith("http")) icon = "https://chatp.net" + icon;

            let tag = "";
            if(isMe) tag = `<span class="tag tag-bot">ME</span>`;
            if(isTarget) tag = `<span class="tag tag-target">TARGET</span>`;

            let row = document.createElement("div");
            row.className = "user-row";
            // CLICK TO TARGET
            row.onclick = function() { selectTarget(name); };
            
            row.innerHTML = `
                <div class="u-left">
                    <img src="${icon}" class="u-pic">
                    <span class="u-name" style="color:${isMe ? 'var(--primary)' : 'white'}">${name}</span>
                </div>
                ${tag}
            `;
            box.appendChild(row);
        });
    }

    function updateBotList() {
        let box = document.getElementById("botList");
        box.innerHTML = "";
        document.getElementById("botCount").innerText = bots.length;

        bots.forEach(b => {
            let color = b.joined ? "lime" : "red";
            let status = b.joined ? "ONLINE" : "WAITING";
            
            let row = document.createElement("div");
            row.className = "user-row";
            row.innerHTML = `
                <span style="font-size:11px;">${b.user}</span>
                <span class="tag" style="border:1px solid ${color}; color:${color}">${status}</span>
            `;
            box.appendChild(row);
        });
    }

    function downloadChat() {
        if(chatLogs.length === 0) { alert("No logs!"); return; }
        let blob = new Blob([chatLogs.join("\\n")], { type: "text/plain" });
        let link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "nexus_logs.txt";
        link.click();
    }

    // --- BOT LOGIC (Method A) ---
    const ASCII = ["(｡♥‿♥｡)", "ʕ•ᴥ•ʔ", "🔥", "❤️", "⚡", "🚀", "💀", "⛔"];

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

                // 1. LOGIN OK
                if(data.handler === "login_event" && data.type === "success") {
                    this.send({ handler: "room_join", id: genId(), name: this.room });
                }
                
                // 2. JOINED ROOM (METHOD A FIX)
                else if(data.handler === "room_event" && data.type === "room_joined") {
                    this.joined = true;
                    updateBotList();
                }

                // 3. MASTER BOT LISTENER (Only one bot updates UI)
                if(this.isMaster) {
                    
                    // ROSTER LIST (On Join)
                    if(data.handler === "room_event" && data.type === "you_joined") {
                        if(data.users) {
                            data.users.forEach(u => usersMap.set(u.username, u));
                            renderUsers();
                        }
                    }
                    
                    // LIVE JOIN/LEAVE
                    if(data.handler === "room_event" && data.type === "join") {
                        usersMap.set(data.username, data); renderUsers();
                    }
                    if(data.handler === "room_event" && data.type === "leave") {
                        usersMap.delete(data.username); renderUsers();
                    }

                    // CHAT LISTENER (For Copycat)
                    if(data.handler === "room_event" && data.type === "text") {
                        log(`${data.from}: ${data.body}`, "log-chat");
                        
                        let mode = document.getElementById("msgMode").value;
                        let target = document.getElementById("targetUser").value;
                        
                        // Copycat Logic
                        if(isSpamming && mode === "copycat" && data.from === target) {
                            forceBroadcast(data.body);
                        }
                    }
                }
            };

            this.ws.onclose = () => {
                this.joined = false;
                updateBotList();
            };
        }

        send(json) {
            if(this.ws && this.ws.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(json));
        }

        sendMessage(txt) {
            if(!this.joined) return;
            // STANDARD PAYLOAD (FIXED)
            this.send({
                handler: "room_message", id: genId(), room: this.room,
                type: "text", body: txt, url: "", length: ""
            });
        }
        
        disconnect() { if(this.ws) this.ws.close(); }
    }

    // --- SYSTEM CONTROLS ---

    function connectArmy() {
        if(isConnected) return;
        
        let room = document.getElementById("roomName").value;
        let raw = document.getElementById("accString").value;
        if(!raw.includes("#")) { alert("No Bots!"); return; }

        usersMap.clear(); myBotNames = []; bots = [];
        renderUsers(); updateBotList();

        let list = raw.split("@").filter(s => s.includes("#"));
        
        list.forEach((s, i) => {
            let [u, p] = s.split("#");
            let cleanU = u.trim();
            myBotNames.push(cleanU);
            
            let isMaster = (i === 0);
            let bot = new Bot(cleanU, p.trim(), room, isMaster);
            bots.push(bot);
            
            setTimeout(() => bot.connect(), i * 500);
        });

        isConnected = true;
        log(`[*] Connecting ${list.length} bots...`);
    }

    function startAttack() {
        if(!isConnected) { alert("Connect First!"); return; }
        if(isSpamming) return;

        isSpamming = true;
        let speed = parseInt(document.getElementById("spamSpeed").value);
        log("🔥 ATTACK STARTED", "log-sys");

        spamInterval = setInterval(() => {
            if(!isSpamming) return;
            
            let mode = document.getElementById("msgMode").value;
            // Copycat is event based, not interval based
            if(mode === "copycat") return; 

            let txt = document.getElementById("customMsg").value || ".";
            let msg = (mode === "ascii") ? ASCII[Math.floor(Math.random()*ASCII.length)] : txt;
            
            forceBroadcast(msg);

        }, speed);
    }

    function forceBroadcast(msg) {
        let burst = parseInt(document.getElementById("burstCount").value);
        
        bots.forEach(b => {
            if(b.joined) {
                for(let i=0; i<burst; i++) {
                    b.sendMessage(msg);
                }
            }
        });
    }

    function stopAttack() {
        isSpamming = false;
        clearInterval(spamInterval);
        log("⏸️ PAUSED", "log-sys");
    }

    function disconnectAll() {
        stopAttack();
        isConnected = false;
        bots.forEach(b => b.disconnect());
        bots = [];
        usersMap.clear();
        myBotNames = [];
        updateBotList();
        renderUsers();
        log("❌ DISCONNECTED ALL", "log-sys");
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
