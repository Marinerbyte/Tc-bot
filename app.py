from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS PRIME CYBER</title>
    <style>
        :root {
            --bg: #050505;
            --panel: rgba(20, 20, 20, 0.95);
            --border: #333;
            --primary: #00ff41; /* Hacker Green */
            --danger: #ff003c;  /* Cyber Red */
            --warn: #fcee0a;    /* Cyber Yellow */
            --accent: #00e5ff;  /* Cyan */
            --text: #e0e0e0;
        }

        body { 
            background-color: var(--bg); 
            background-image: radial-gradient(circle at 50% 50%, #111 0%, #000 100%);
            color: var(--text); 
            font-family: 'Segoe UI', 'Roboto', monospace; 
            margin: 0; padding: 10px; 
            height: 100vh; 
            display: flex; flex-direction: column;
            overflow: hidden;
        }

        /* SCROLLBAR */
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: #000; }
        ::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 3px; }

        /* HEADER */
        header {
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid var(--primary); padding-bottom: 10px; margin-bottom: 10px;
            text-transform: uppercase; letter-spacing: 2px;
        }
        h1 { margin: 0; font-size: 18px; color: var(--primary); text-shadow: 0 0 10px var(--primary); }

        /* GRID LAYOUT */
        .main-grid {
            display: grid; 
            grid-template-columns: 280px 1fr 250px; 
            gap: 10px; 
            flex: 1; 
            overflow: hidden;
        }
        @media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; grid-template-rows: auto auto auto; overflow-y: auto; } }

        /* PANELS */
        .card {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px;
            display: flex; flex-direction: column;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
        }
        .card-header {
            font-size: 12px; font-weight: bold; color: var(--accent);
            border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 10px;
            display: flex; justify-content: space-between;
        }

        /* INPUTS */
        label { font-size: 10px; color: #888; display: block; margin-top: 8px; }
        input, textarea, select {
            width: 100%; background: #0a0a0a; border: 1px solid #444; color: white;
            padding: 8px; margin-top: 2px; border-radius: 4px; font-family: monospace; font-size: 11px;
            box-sizing: border-box; transition: 0.3s;
        }
        input:focus, textarea:focus { border-color: var(--primary); outline: none; box-shadow: 0 0 5px var(--primary); }
        textarea { height: 60px; resize: none; color: var(--warn); }

        /* BUTTONS */
        .btn-group { display: flex; gap: 5px; margin-top: 10px; }
        button {
            flex: 1; padding: 10px; border: none; border-radius: 4px;
            font-weight: bold; cursor: pointer; font-size: 11px; text-transform: uppercase;
            transition: 0.2s;
        }
        button:active { transform: scale(0.98); }
        .btn-green { background: linear-gradient(45deg, #004d00, #008000); color: white; border: 1px solid var(--primary); }
        .btn-red { background: linear-gradient(45deg, #4d0000, #800000); color: white; border: 1px solid var(--danger); }
        .btn-blue { background: linear-gradient(45deg, #00224d, #004480); color: white; border: 1px solid var(--accent); }
        .btn-sm { padding: 4px 8px; font-size: 9px; width: auto; margin: 0; }

        /* LISTS */
        .list-box { flex: 1; overflow-y: auto; font-size: 11px; }
        .list-item { 
            display: flex; align-items: center; justify-content: space-between; 
            padding: 4px; border-bottom: 1px solid #222; 
        }
        .list-item:hover { background: #1a1a1a; }
        
        .u-pic { width: 24px; height: 24px; border-radius: 50%; margin-right: 8px; border: 1px solid #444; }
        .u-info { display: flex; align-items: center; }
        .u-tag { font-size: 8px; padding: 1px 4px; border-radius: 3px; margin-left: 5px; }
        .tag-bot { background: var(--primary); color: black; }
        .tag-target { background: var(--danger); color: white; animation: pulse 1s infinite; }

        /* LOGS */
        .log-box { font-family: monospace; font-size: 10px; color: #aaa; }
        .log-entry { margin-bottom: 2px; padding-left: 5px; border-left: 2px solid #333; }
        .log-chat { color: var(--accent); border-left-color: var(--accent); }
        .log-sys { color: #888; }
        .log-err { color: var(--danger); border-left-color: var(--danger); }

        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
</head>
<body>

<header>
    <h1>⚡ NEXUS PRIME</h1>
    <div style="font-size: 10px; color: #888;">STATUS: <span id="sysStatus" style="color:var(--primary)">READY</span></div>
</header>

<div class="main-grid">

    <!-- LEFT: CONFIGURATION -->
    <div class="card">
        <div class="card-header">
            <span>📡 CONNECTION</span>
            <button class="btn-sm btn-red" onclick="clearInput('accString')">CLEAR</button>
        </div>
        
        <label>🎯 TARGET ROOM</label>
        <input type="text" id="roomName" value="ملتقى🥂العرب">

        <label>💂 BOT ACCOUNTS (user#pass@...)</label>
        <textarea id="accString" placeholder="bot1#pass123@bot2#pass123@"></textarea>

        <button class="btn-blue" style="margin-top:10px;" onclick="connectArmy()">🔌 CONNECT ARMY</button>

        <div class="card-header" style="margin-top: 20px;">
            <span>🤖 MY BOTS (<span id="botCount">0</span>)</span>
        </div>
        <div id="myBotList" class="list-box" style="max-height: 150px;"></div>
    </div>

    <!-- CENTER: ATTACK CONSOLE -->
    <div class="card">
        <div class="card-header">⚔️ ATTACK CONSOLE</div>

        <div style="display:flex; gap:10px;">
            <div style="flex:1">
                <label>⚡ SPEED (ms)</label>
                <input type="number" id="spamSpeed" value="2000">
            </div>
            <div style="flex:1">
                <label>💥 BURST (Msg/Tick)</label>
                <input type="number" id="burstCount" value="1">
            </div>
        </div>

        <div style="display:flex; gap:10px;">
            <div style="flex:1">
                <label>🎭 MODE</label>
                <select id="msgMode" onchange="toggleCopycat()">
                    <option value="custom">✍️ Custom Text</option>
                    <option value="ascii">🎲 Random ASCII</option>
                    <option value="copycat">🦜 Copycat (Mimic)</option>
                </select>
            </div>
            <div style="flex:1">
                <label>🎯 TARGET USER</label>
                <input type="text" id="targetUser" placeholder="Username..." disabled style="opacity:0.5;">
            </div>
        </div>

        <label>💬 MESSAGE CONTENT</label>
        <input type="text" id="customMsg" placeholder="Type here...">

        <div class="btn-group">
            <button class="btn-green" onclick="startAttack()">🔥 START ATTACK</button>
            <button class="btn-red" onclick="stopAttack()">⏸️ PAUSE</button>
        </div>

        <div class="card-header" style="margin-top:15px;">
            <span>📜 LIVE TERMINAL</span>
            <button class="btn-sm btn-red" onclick="document.getElementById('logs').innerHTML=''">CLR</button>
        </div>
        <div id="logs" class="list-box log-box"></div>
    </div>

    <!-- RIGHT: INTELLIGENCE -->
    <div class="card">
        <div class="card-header">
            <span>👥 ROOM USERS (<span id="uCount">0</span>)</span>
            <button class="btn-sm btn-blue" onclick="downloadChat()">💾 SAVE CHAT</button>
        </div>
        <div id="userList" class="list-box"></div>
    </div>

</div>

<script>
    // --- CORE VARIABLES ---
    let bots = [];
    let isConnected = false;
    let isSpamming = false;
    let spamInterval = null;
    
    let usersMap = new Map();   // Room Users
    let myBotMap = new Map();   // My Connected Bots
    let targetLogs = [];        // Logs for export

    // --- UTILITIES ---
    function log(msg, type="log-sys") {
        let box = document.getElementById("logs");
        let d = document.createElement("div");
        d.className = "log-entry " + type;
        d.innerText = `> ${msg}`;
        box.prepend(d);
    }

    function genId(len=20) {
        let c="abcdef0123456789", s="";
        for(let i=0; i<len; i++) s += c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    function clearInput(id) { document.getElementById(id).value = ""; }

    function toggleCopycat() {
        let mode = document.getElementById("msgMode").value;
        let input = document.getElementById("targetUser");
        if(mode === "copycat") {
            input.disabled = false; input.style.opacity = "1"; input.style.borderColor = "var(--danger)";
        } else {
            input.disabled = true; input.style.opacity = "0.5"; input.style.borderColor = "#444";
        }
    }

    // --- UI RENDERERS ---
    
    function renderMyBots() {
        let box = document.getElementById("myBotList");
        box.innerHTML = "";
        document.getElementById("botCount").innerText = myBotMap.size;

        myBotMap.forEach((status, user) => {
            let color = status === "ONLINE" ? "lime" : "red";
            let div = document.createElement("div");
            div.className = "list-item";
            div.innerHTML = `<span>${user}</span> <span style="color:${color}; font-size:9px;">${status}</span>`;
            box.appendChild(div);
        });
    }

    function renderRoomUsers() {
        let box = document.getElementById("userList");
        box.innerHTML = "";
        document.getElementById("uCount").innerText = usersMap.size;
        let target = document.getElementById("targetUser").value;

        usersMap.forEach((u) => {
            let name = u.name || u.username || "Unknown";
            let icon = u.avatar_url || u.icon || "https://ui-avatars.com/api/?name="+name;
            if(!icon.startsWith("http")) icon = "https://chatp.net" + icon;

            let isBot = myBotMap.has(name);
            let isTarget = (name === target);
            
            let tagHTML = "";
            if(isBot) tagHTML = `<span class="u-tag tag-bot">ME</span>`;
            if(isTarget) tagHTML = `<span class="u-tag tag-target">TARGET</span>`;

            let div = document.createElement("div");
            div.className = "list-item";
            div.onclick = function() { document.getElementById("targetUser").value = name; toggleCopycat(); renderRoomUsers(); };
            div.innerHTML = `
                <div class="u-info">
                    <img src="${icon}" class="u-pic">
                    <span style="color:${isBot?'var(--primary)':'white'}">${name}</span>
                    ${tagHTML}
                </div>
            `;
            box.appendChild(div);
        });
    }

    // --- DOWNLOAD CHAT ---
    function downloadChat() {
        if(targetLogs.length === 0) { alert("No logs to save!"); return; }
        let content = "--- CHAT LOGS ---\\n" + targetLogs.join("\\n");
        let blob = new Blob([content], { type: "text/plain" });
        let a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "chat_log.txt";
        a.click();
    }

    // --- BOT CLASS ---
    const ASCII = ["(｡♥‿♥｡)", "ʕ•ᴥ•ʔ", "🔥", "❤️", "⚡", "🚀", "💀", "⛔", "⚠️"];

    class Bot {
        constructor(user, pass, room, isMaster) {
            this.user = user;
            this.pass = pass;
            this.room = room;
            this.ws = null;
            this.joined = false;
            this.isMaster = isMaster; // Master handles Chat Listening
        }

        connect() {
            if(this.ws) return;
            
            this.ws = new WebSocket("wss://chatp.net:5333/server");

            this.ws.onopen = () => {
                myBotMap.set(this.user, "CONNECTING"); renderMyBots();
                this.send({ handler: "login", id: genId(), username: this.user, password: this.pass });
            };

            this.ws.onmessage = (e) => {
                let data = JSON.parse(e.data);

                // 1. LOGIN OK
                if(data.handler === "login_event" && data.type === "success") {
                    this.send({ handler: "room_join", id: genId(), name: this.room });
                }
                
                // 2. JOINED
                else if(data.handler === "room_event" && data.type === "room_joined") {
                    this.joined = true;
                    myBotMap.set(this.user, "ONLINE"); renderMyBots();
                }

                // 3. LISTENERS (MASTER ONLY)
                if(this.isMaster) {
                    // ROSTER
                    if((data.handler === "roster" || data.handler === "room_users") && data.users) {
                        data.users.forEach(u => usersMap.set(u.username, u));
                        renderRoomUsers();
                    }
                    if(data.handler === "room_event" && data.type === "join") {
                        usersMap.set(data.username, data); renderRoomUsers();
                    }
                    if(data.handler === "room_event" && data.type === "leave") {
                        usersMap.delete(data.username); renderRoomUsers();
                    }

                    // CHAT & COPYCAT TRIGGER
                    if(data.handler === "room_event" && data.type === "text") {
                        let sender = data.from;
                        let msg = data.body;
                        
                        log(`${sender}: ${msg}`, "log-chat");
                        targetLogs.push(`[${new Date().toLocaleTimeString()}] ${sender}: ${msg}`);

                        // COPYCAT LOGIC
                        let mode = document.getElementById("msgMode").value;
                        let target = document.getElementById("targetUser").value;
                        
                        if(mode === "copycat" && isSpamming && sender === target) {
                            forceBroadcast(msg); // All bots repeat what target said
                        }
                    }
                }
            };

            this.ws.onclose = () => {
                this.joined = false;
                myBotMap.set(this.user, "OFFLINE"); renderMyBots();
            };
        }

        send(json) {
            if(this.ws && this.ws.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(json));
        }

        sendMessage(txt) {
            if(!this.joined) return;
            // Method A Payload
            this.send({
                handler: "room_message", id: genId(), room: this.room,
                type: "text", body: txt, url: "", length: ""
            });
        }
        
        disconnect() { if(this.ws) this.ws.close(); }
    }

    // --- CONTROL CENTER ---

    function connectArmy() {
        if(isConnected) return;
        
        let room = document.getElementById("roomName").value;
        let raw = document.getElementById("accString").value;
        if(!raw.includes("#")) { alert("No Bots!"); return; }

        usersMap.clear(); myBotMap.clear(); bots = [];
        renderRoomUsers(); renderMyBots();

        let list = raw.split("@").filter(s => s.includes("#"));
        
        list.forEach((s, i) => {
            let [u, p] = s.split("#");
            let isMaster = (i === 0); // First bot is master
            let bot = new Bot(u.trim(), p.trim(), room, isMaster);
            bots.push(bot);
            setTimeout(() => bot.connect(), i * 500);
        });

        isConnected = true;
        log("System Initialized...");
    }

    function startAttack() {
        if(!isConnected) { alert("Connect First!"); return; }
        if(isSpamming) return;

        isSpamming = true;
        let speed = parseInt(document.getElementById("spamSpeed").value);
        log("🔥 ATTACK SEQUENCE STARTED", "log-sys");

        spamInterval = setInterval(() => {
            if(!isSpamming) return;
            
            let mode = document.getElementById("msgMode").value;
            // Copycat is event-driven, not interval-driven
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
                // Burst Loop
                for(let i=0; i<burst; i++) {
                    b.sendMessage(msg);
                }
            }
        });
    }

    function stopAttack() {
        isSpamming = false;
        clearInterval(spamInterval);
        log("⏸️ ATTACK PAUSED");
    }

    function disconnectAll() {
        stopAttack();
        isConnected = false;
        bots.forEach(b => b.disconnect());
        bots = [];
        log("❌ DISCONNECTED ALL");
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
