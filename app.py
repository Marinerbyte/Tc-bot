from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NEXUS TRINITY</title>
    <style>
        /* --- CYBER THEME --- */
        :root {
            --bg: #000000;
            --panel: #0d0d0d;
            --border: #333;
            --primary: #00ff00; /* Hacker Green */
            --spy: #00ccff;     /* Cyan for Spy */
            --attack: #ff0000;  /* Red for Attack */
            --text: #ffffff;
        }

        body { 
            background-color: var(--bg); color: var(--text); 
            font-family: 'Courier New', monospace; margin: 0; padding: 0;
            height: 100vh; display: flex; flex-direction: column; overflow: hidden;
        }

        /* TOP NAVIGATION (THE SEPARATOR) */
        nav {
            display: flex; height: 50px; border-bottom: 2px solid #222;
        }
        .nav-item {
            flex: 1; display: flex; align-items: center; justify-content: center;
            font-weight: bold; font-size: 14px; cursor: pointer;
            border-right: 1px solid #222; transition: 0.2s; text-transform: uppercase;
        }
        .nav-home { color: var(--primary); background: #051a05; }
        .nav-attack { color: #555; background: #111; }
        .nav-spy { color: #555; background: #111; }

        /* ACTIVE STATES */
        .nav-attack.active { background: #220000; color: var(--attack); box-shadow: inset 0 -3px 0 var(--attack); }
        .nav-spy.active { background: #001122; color: var(--spy); box-shadow: inset 0 -3px 0 var(--spy); }
        .nav-home.active { background: #002200; color: var(--primary); box-shadow: inset 0 -3px 0 var(--primary); }

        /* PAGES */
        .page { display: none; padding: 10px; height: calc(100vh - 60px); overflow-y: auto; }
        .page.active { display: block; animation: fadeIn 0.3s; }

        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

        /* COMPONENTS */
        .box { border: 1px solid var(--border); background: var(--panel); padding: 10px; margin-bottom: 10px; border-radius: 4px; }
        .box-title { font-size: 12px; font-weight: bold; border-bottom: 1px dashed #444; padding-bottom: 5px; margin-bottom: 10px; display: block; }
        
        input, textarea, select {
            width: 100%; background: #000; border: 1px solid #444; color: #fff;
            padding: 10px; margin-top: 5px; box-sizing: border-box; font-family: monospace;
        }
        textarea { height: 100px; color: yellow; font-size: 11px; }

        button {
            width: 100%; padding: 12px; font-weight: bold; cursor: pointer; 
            border: none; margin-top: 10px; font-size: 12px; text-transform: uppercase;
        }
        
        /* COLORS */
        .btn-green { background: #006400; color: white; border: 1px solid var(--primary); }
        .btn-red { background: #640000; color: white; border: 1px solid var(--attack); }
        .btn-cyan { background: #004d66; color: white; border: 1px solid var(--spy); }

        /* LISTS */
        .scroll-view { height: 200px; overflow-y: scroll; background: #000; border: 1px solid #222; padding: 5px; font-size: 11px; }
        
        .user-row { display: flex; align-items: center; justify-content: space-between; padding: 5px; border-bottom: 1px solid #111; cursor: pointer; }
        .user-row:hover { background: #111; }
        .u-pic { width: 24px; height: 24px; border-radius: 50%; border: 1px solid #333; margin-right: 10px; }
        
        .chat-row { padding: 4px; border-bottom: 1px solid #1a1a1a; font-size: 11px; }
        .chat-time { color: #555; font-size: 9px; margin-right: 5px; }
        .chat-name { font-weight: bold; color: var(--spy); }
        
        /* STATUS BADGES */
        .status-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2px; }
        .badge { font-size: 9px; padding: 3px; text-align: center; border: 1px solid #333; }
        .on { color: lime; border-color: lime; }
        .off { color: red; border-color: red; }

    </style>
</head>
<body>

<nav>
    <div class="nav-item nav-home active" onclick="showPage('home')">1. DASHBOARD</div>
    <div class="nav-item nav-attack" onclick="showPage('attack')">2. ATTACK</div>
    <div class="nav-item nav-spy" onclick="showPage('spy')">3. SPY</div>
</nav>

<!-- PAGE 1: CONNECTION DASHBOARD -->
<div id="home" class="page active">
    <div class="box">
        <span class="box-title" style="color:var(--primary)">📡 CONNECTION CENTER</span>
        
        <label>Room Name:</label>
        <input type="text" id="roomName" value="ملتقى🥂العرب">
        
        <label>Accounts (user#pass@...):</label>
        <textarea id="accString" placeholder="bot1#pass123@bot2#pass123@"></textarea>
        
        <button class="btn-green" onclick="connectSystem()">🔌 INITIALIZE BOTS</button>
        <button class="btn-red" onclick="killSystem()">❌ TERMINATE ALL</button>
    </div>

    <div class="box">
        <span class="box-title">🤖 BOT STATUS GRID</span>
        <div id="botGrid" class="status-grid"></div>
        <div style="font-size:10px; text-align:center; margin-top:5px; color:#666;">Total: <span id="botCount">0</span></div>
    </div>

    <div class="box">
        <span class="box-title">📜 SYSTEM LOGS</span>
        <div id="sysLogs" class="scroll-view" style="height:100px; color:#888;"></div>
    </div>
</div>

<!-- PAGE 2: ATTACK PANEL -->
<div id="attack" class="page">
    <div class="box" style="border-color: var(--attack);">
        <span class="box-title" style="color:var(--attack)">⚔️ WEAPON SYSTEM</span>
        
        <div style="display:flex; gap:5px;">
            <input type="number" id="spamSpeed" value="2000" placeholder="Speed (ms)">
            <input type="number" id="burstCount" value="1" placeholder="Burst (1-5)">
        </div>

        <select id="msgMode">
            <option value="custom">✍️ Custom Text</option>
            <option value="ascii">🎲 Random ASCII</option>
        </select>

        <input type="text" id="spamText" placeholder="Enter spam message...">

        <button class="btn-red" id="btnAttack" onclick="toggleAttack()">🔥 START FIRE</button>
    </div>
    
    <div class="box">
        <span class="box-title">STATUS</span>
        <div id="attackStatus" style="text-align:center; color:#444;">IDLE</div>
    </div>
</div>

<!-- PAGE 3: SPY PANEL -->
<div id="spy" class="page">
    <div class="box" style="border-color: var(--spy);">
        <span class="box-title" style="color:var(--spy)">👁️ TARGET ACQUISITION</span>
        
        <input type="text" id="targetName" placeholder="Select User below..." readonly 
               style="border-color:var(--spy); color:var(--spy); font-weight:bold; cursor:not-allowed;">
        
        <div style="display:flex; gap:5px; margin-top:5px;">
            <button class="btn-cyan" id="btnCopycat" onclick="toggleCopycat()">🦜 START COPYCAT</button>
            <button class="btn-green" onclick="exportChat()">💾 DOWNLOAD CHAT</button>
        </div>
        <button class="btn-red" style="margin-top:5px;" onclick="clearSpy()">🗑️ CLEAR</button>
    </div>

    <div class="box">
        <span class="box-title">📡 INTERCEPTED CHAT</span>
        <div id="spyBox" class="scroll-view" style="height:150px;"></div>
    </div>

    <div class="box">
        <span class="box-title">👥 ROOM USERS (<span id="userCount">0</span>)</span>
        <div id="userList" class="scroll-view"></div>
    </div>
</div>

<script>
    // --- CORE SYSTEM ---
    let bots = [];
    let isConnected = false;
    let attackInterval = null;
    let copycatEnabled = false;
    let targetUser = null;
    
    let usersMap = new Map(); // Room Users
    let capturedLogs = [];    // For export

    // --- NAVIGATION ---
    function showPage(pageId) {
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        
        document.getElementById(pageId).classList.add('active');
        document.querySelector(`.nav-${pageId}`).classList.add('active');
    }

    // --- LOGGING ---
    function log(msg) {
        let box = document.getElementById("sysLogs");
        let d = document.createElement("div");
        d.innerText = "> " + msg;
        box.prepend(d);
    }

    function genId(len=20) {
        let c="abcdef0123456789", s="";
        for(let i=0; i<len; i++) s += c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    // --- UI UPDATES ---
    function updateBotGrid() {
        let grid = document.getElementById("botGrid");
        grid.innerHTML = "";
        document.getElementById("botCount").innerText = bots.length;

        bots.forEach(b => {
            let cls = b.joined ? "on" : "off";
            let d = document.createElement("div");
            d.className = `badge ${cls}`;
            d.innerText = b.user;
            grid.appendChild(d);
        });
    }

    function renderUserList() {
        let box = document.getElementById("userList");
        box.innerHTML = "";
        document.getElementById("userCount").innerText = usersMap.size;

        usersMap.forEach(u => {
            let name = u.username || u.name || "Unknown";
            let icon = u.avatar_url || u.icon || "https://ui-avatars.com/api/?name="+name;
            if(!icon.startsWith("http")) icon = "https://chatp.net" + icon;

            let row = document.createElement("div");
            row.className = "user-row";
            row.onclick = () => selectTarget(name);
            row.innerHTML = `
                <div style="display:flex; align-items:center;">
                    <img src="${icon}" class="u-pic">
                    <span style="color:${name === targetUser ? 'var(--spy)' : 'white'}">${name}</span>
                </div>
                <div style="font-size:9px; color:#555;">TAP TO SPY</div>
            `;
            box.appendChild(row);
        });
    }

    // --- SPY FUNCTIONS ---
    function selectTarget(name) {
        targetUser = name;
        document.getElementById("targetName").value = name;
        log(`Target Locked: ${name}`);
        renderUserList(); // Update highlight
    }

    function addToSpyLog(name, msg) {
        let box = document.getElementById("spyBox");
        let time = new Date().toLocaleTimeString();
        
        // UI
        let d = document.createElement("div");
        d.className = "chat-row";
        d.innerHTML = `<span class="chat-time">${time}</span><span class="chat-name">${name}:</span> <span style="color:#ddd">${msg}</span>`;
        box.prepend(d);

        // Memory
        capturedLogs.push(`[${time}] ${name}: ${msg}`);
    }

    function exportChat() {
        if(capturedLogs.length === 0) { alert("Empty!"); return; }
        // FIX: UTF-8 BOM
        let content = "\ufeff" + capturedLogs.join("\\n");
        let blob = new Blob([content], { type: "text/plain;charset=utf-8" });
        let url = URL.createObjectURL(blob);
        let a = document.createElement("a");
        a.href = url;
        a.download = `spy_${targetUser || 'log'}.txt`;
        a.click();
    }

    function clearSpy() {
        capturedLogs = [];
        document.getElementById("spyBox").innerHTML = "";
    }

    // --- BOT CLASS ---
    const ASCII = ["(｡♥‿♥｡)", "ʕ•ᴥ•ʔ", "🔥", "❤️", "⚡", "🚀", "💀"];

    class Bot {
        constructor(user, pass, room, isMaster) {
            this.user = user;
            this.pass = pass;
            this.room = room;
            this.ws = null;
            this.joined = false;
            this.isMaster = isMaster; // Only 1st bot listens
        }

        connect() {
            if(this.ws) return;
            this.ws = new WebSocket("wss://chatp.net:5333/server");

            this.ws.onopen = () => {
                this.send({ handler: "login", id: genId(), username: this.user, password: this.pass });
            };

            this.ws.onmessage = (e) => {
                let data = JSON.parse(e.data);

                // LOGIN OK
                if(data.handler === "login_event" && data.type === "success") {
                    this.send({ handler: "room_join", id: genId(), name: this.room });
                }
                
                // JOINED
                else if(data.handler === "room_event" && data.type === "room_joined") {
                    this.joined = true;
                    updateBotGrid();
                }

                // --- MASTER BOT INTELLIGENCE ---
                if(this.isMaster) {
                    
                    // 1. ROSTER (Initial User List)
                    // Server sends 'you_joined' with users array
                    if(data.handler === "room_event" && data.type === "you_joined") {
                        if(data.users) {
                            data.users.forEach(u => usersMap.set(u.username, u));
                            renderUserList();
                        }
                    }

                    // 2. LIVE JOIN/LEAVE
                    if(data.handler === "room_event" && data.type === "join") {
                        usersMap.set(data.username, data); renderUserList();
                    }
                    if(data.handler === "room_event" && data.type === "leave") {
                        usersMap.delete(data.username); renderUserList();
                    }

                    // 3. CHAT MONITOR (Spy & Copycat)
                    if(data.handler === "room_event" && data.type === "text") {
                        // Capture target messages
                        if(data.from === targetUser) {
                            addToSpyLog(data.from, data.body);
                            
                            // Trigger Copycat
                            if(copycatEnabled) {
                                bots.forEach(b => { 
                                    if(b.joined) b.sendMessage(data.body); 
                                });
                            }
                        }
                    }
                }
            };

            this.ws.onclose = () => {
                this.joined = false;
                updateBotGrid();
            };
        }

        send(json) {
            if(this.ws && this.ws.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(json));
        }

        sendMessage(txt) {
            if(!this.joined) return;
            // METHOD A PAYLOAD
            this.send({
                handler: "room_message", id: genId(), room: this.room,
                type: "text", body: txt, url: "", length: ""
            });
        }
        
        disconnect() { if(this.ws) this.ws.close(); }
    }

    // --- CONTROLLERS ---

    function connectSystem() {
        if(isConnected) return;
        let room = document.getElementById("roomName").value;
        let raw = document.getElementById("accString").value;
        if(!raw.includes("#")) { alert("No Bots!"); return; }

        usersMap.clear(); bots = [];
        renderUserList(); updateBotGrid();

        let list = raw.split("@").filter(s => s.includes("#"));
        
        list.forEach((s, i) => {
            let [u, p] = s.split("#");
            let isMaster = (i === 0);
            let bot = new Bot(u.trim(), p.trim(), room, isMaster);
            bots.push(bot);
            setTimeout(() => bot.connect(), i * 600);
        });

        isConnected = true;
        log(`Connecting ${list.length} bots...`);
    }

    function toggleAttack() {
        let btn = document.getElementById("btnAttack");
        let status = document.getElementById("attackStatus");

        if(attackInterval) {
            // STOP
            clearInterval(attackInterval);
            attackInterval = null;
            btn.innerText = "🔥 START FIRE";
            btn.classList.replace("btn-red", "btn-green"); // Make green again
            status.innerText = "IDLE";
            status.style.color = "#444";
        } else {
            // START
            if(!isConnected) { alert("Connect First!"); return; }
            let speed = parseInt(document.getElementById("spamSpeed").value);
            
            btn.innerText = "⏸️ STOP FIRE";
            btn.classList.replace("btn-green", "btn-red"); // Make red
            status.innerText = "FIRING...";
            status.style.color = "var(--attack)";

            attackInterval = setInterval(() => {
                let mode = document.getElementById("msgMode").value;
                let txt = document.getElementById("spamText").value || ".";
                let burst = parseInt(document.getElementById("burstCount").value);
                let msg = (mode === "ascii") ? ASCII[Math.floor(Math.random()*ASCII.length)] : txt;

                bots.forEach(b => {
                    if(b.joined) {
                        for(let k=0; k<burst; k++) b.sendMessage(msg);
                    }
                });
            }, speed);
        }
    }

    function toggleCopycat() {
        copycatEnabled = !copycatEnabled;
        let btn = document.getElementById("btnCopycat");
        if(copycatEnabled) {
            btn.innerText = "🦜 STOP COPY";
            btn.style.border = "1px solid var(--attack)";
        } else {
            btn.innerText = "🦜 START COPYCAT";
            btn.style.border = "1px solid var(--spy)";
        }
    }

    function killSystem() {
        if(attackInterval) toggleAttack(); // Stop spam
        bots.forEach(b => b.disconnect());
        bots = [];
        isConnected = false;
        usersMap.clear();
        updateBotGrid();
        renderUserList();
        log("System Terminated.");
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
