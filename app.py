from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NEXUS SURVEILLANCE</title>
    <style>
        /* --- CORE THEME --- */
        :root {
            --bg: #050505;
            --panel: #0f0f0f;
            --border: #333;
            --primary: #00ff41; /* Matrix Green */
            --secondary: #00e5ff; /* Cyan */
            --danger: #ff003c; /* Red */
            --warn: #ffcc00; /* Yellow */
            --text: #e0e0e0;
        }

        body { 
            background-color: var(--bg); 
            color: var(--text); 
            font-family: 'Consolas', monospace; 
            margin: 0; padding: 0;
            height: 100vh; display: flex; flex-direction: column;
        }

        /* NAVIGATION TABS */
        .nav-bar {
            display: flex; background: #000; border-bottom: 2px solid var(--primary);
        }
        .nav-btn {
            flex: 1; padding: 15px; background: #111; color: #666; 
            border: none; border-right: 1px solid #222; cursor: pointer; font-weight: bold;
            font-size: 11px; transition: 0.3s;
        }
        .nav-btn.active { background: #002200; color: var(--primary); border-bottom: 2px solid var(--primary); }

        /* CONTENT PAGES */
        .tab-content { display: none; padding: 10px; overflow-y: auto; flex: 1; }
        .tab-content.active { display: block; }

        /* CARDS & INPUTS */
        .card {
            background: var(--panel); border: 1px solid var(--border);
            padding: 10px; margin-bottom: 10px; border-radius: 4px;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }
        .card-header {
            color: var(--primary); font-size: 12px; font-weight: bold;
            border-bottom: 1px dashed #333; padding-bottom: 5px; margin-bottom: 10px;
            display: flex; justify-content: space-between; align-items: center;
        }

        label { font-size: 10px; color: #888; display: block; margin-top: 8px; }
        input, textarea, select {
            width: 100%; background: #000; border: 1px solid #444; color: white;
            padding: 10px; margin-top: 3px; border-radius: 3px; font-family: monospace;
            box-sizing: border-box; outline: none;
        }
        input:focus { border-color: var(--secondary); }
        textarea { height: 60px; color: var(--warn); }

        /* BUTTONS */
        .btn-row { display: flex; gap: 5px; margin-top: 10px; }
        button {
            flex: 1; padding: 12px; border: none; border-radius: 3px;
            font-weight: bold; font-size: 11px; cursor: pointer; color: white;
            text-transform: uppercase;
        }
        .btn-green { background: #006400; border: 1px solid var(--primary); }
        .btn-red { background: #640000; border: 1px solid var(--danger); }
        .btn-cyan { background: #004d66; border: 1px solid var(--secondary); }
        .btn-sm { padding: 4px 8px; font-size: 9px; width: auto; flex: none; }

        /* LISTS */
        .scroll-list {
            height: 200px; overflow-y: auto; background: #000; 
            border: 1px solid #222; padding: 5px; margin-top: 5px;
        }
        .list-item { 
            display: flex; align-items: center; justify-content: space-between; 
            padding: 5px; border-bottom: 1px solid #1a1a1a; 
        }
        .u-pic { width: 24px; height: 24px; border-radius: 50%; border: 1px solid #333; margin-right: 8px; }
        .u-name { font-size: 12px; color: #ccc; }
        
        /* TAGS */
        .tag { font-size: 9px; padding: 2px 4px; border-radius: 3px; }
        .tag-on { color: var(--primary); border: 1px solid var(--primary); }
        .tag-off { color: var(--danger); border: 1px solid var(--danger); }
        
        /* SPY BOX */
        .spy-box {
            height: 250px; overflow-y: scroll; background: #050505; border: 1px solid var(--secondary);
            padding: 10px; font-size: 11px; font-family: monospace;
        }
        .spy-msg { margin-bottom: 5px; border-left: 2px solid var(--secondary); padding-left: 8px; }
        .spy-time { color: #555; font-size: 9px; }
        .spy-text { color: #fff; }

    </style>
</head>
<body>

<!-- NAVIGATION -->
<div class="nav-bar">
    <button class="nav-btn active" onclick="switchTab('tab1', this)">1. DASHBOARD</button>
    <button class="nav-btn" onclick="switchTab('tab2', this)">2. ATTACK</button>
    <button class="nav-btn" onclick="switchTab('tab3', this)" style="color:var(--secondary)">3. SPY & COPY</button>
</div>

<!-- TAB 1: CONNECTION & LISTS -->
<div id="tab1" class="tab-content active">
    <div class="card">
        <div class="card-header">📡 CONNECTION</div>
        <label>🎯 TARGET ROOM</label>
        <input type="text" id="roomName" value="ملتقى🥂العرب">
        
        <label>📝 ACCOUNTS (user#pass@...)</label>
        <textarea id="accString" placeholder="bot1#pass123@bot2#pass123@"></textarea>
        
        <div class="btn-row">
            <button class="btn-green" onclick="connectArmy()">🔌 CONNECT ALL</button>
            <button class="btn-red" onclick="disconnectAll()">❌ KILL ALL</button>
        </div>
    </div>

    <div class="card">
        <div class="card-header">
            <span>🤖 CONNECTED BOTS (<span id="botCount">0</span>)</span>
        </div>
        <div id="botList" class="scroll-list" style="height: 120px;"></div>
    </div>

    <div class="card">
        <div class="card-header">
            <span>👥 ROOM USERS (<span id="uCount">0</span>)</span>
            <span style="font-size:9px;">(Tap User to Spy)</span>
        </div>
        <div id="userList" class="scroll-list"></div>
    </div>
</div>

<!-- TAB 2: ATTACK CONTROLS -->
<div id="tab2" class="tab-content">
    <div class="card">
        <div class="card-header">⚔️ SPAM CONFIG</div>
        
        <div style="display:flex; gap:10px;">
            <div style="flex:1">
                <label>⚡ SPEED (ms)</label>
                <input type="number" id="spamSpeed" value="2000">
            </div>
            <div style="flex:1">
                <label>💥 BURST (Msg/Bot)</label>
                <input type="number" id="burstCount" value="1">
            </div>
        </div>

        <label>🎭 MESSAGE MODE</label>
        <select id="msgMode">
            <option value="custom">✍️ Custom Text</option>
            <option value="ascii">🎲 Random ASCII</option>
        </select>

        <label>💬 CONTENT</label>
        <input type="text" id="customMsg" placeholder="Type here...">

        <div class="btn-row">
            <button class="btn-green" onclick="startSpam()">🔥 START SPAM</button>
            <button class="btn-red" onclick="stopSpam()">⏸️ STOP SPAM</button>
        </div>
    </div>
    
    <div class="card">
        <div class="card-header">📜 SYSTEM LOGS</div>
        <div id="sysLogs" class="scroll-list" style="font-size:10px; color:#888;"></div>
    </div>
</div>

<!-- TAB 3: SPY & COPYCAT -->
<div id="tab3" class="tab-content">
    <div class="card" style="border-color: var(--secondary);">
        <div class="card-header" style="color:var(--secondary)">
            <span>👁️ TARGET MONITOR</span>
            <span id="targetStatus" style="color:#555;">NO TARGET</span>
        </div>

        <label>🎯 LOCKED TARGET USER</label>
        <input type="text" id="targetName" placeholder="Select from Dashboard..." readonly style="color:var(--secondary); border-color:var(--secondary);">

        <div class="btn-row">
            <button class="btn-cyan" id="btnCopycat" onclick="toggleCopycat()">🦜 START COPYCAT</button>
            <button class="btn-green" onclick="downloadSpyLogs()">💾 EXPORT CHAT (TXT)</button>
        </div>
        <div class="btn-row">
             <button class="btn-red" onclick="clearSpyLogs()">🗑️ CLEAR HISTORY</button>
        </div>
    </div>

    <div class="card">
        <div class="card-header">📡 INTERCEPTED MESSAGES</div>
        <div id="spyFeed" class="spy-box">
            <div style="text-align:center; color:#444; margin-top:50px;">Waiting for target...</div>
        </div>
    </div>
</div>

<script>
    // --- VARIABLES ---
    let bots = [];
    let usersMap = new Map();
    let myBotNames = [];
    
    // State
    let isConnected = false;
    let isSpamming = false;
    let isCopycat = false;
    let spamInterval = null;
    let targetUser = "";
    
    // Logs
    let spyLogs = []; // Stores Target Chat

    // --- UI LOGIC ---
    function switchTab(id, btn) {
        document.querySelectorAll('.tab-content').forEach(d => d.classList.remove('active'));
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(id).classList.add('active');
        btn.classList.add('active');
    }

    function sysLog(msg) {
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

    // --- RENDERERS ---
    function updateBotUI() {
        let box = document.getElementById("botList");
        box.innerHTML = "";
        document.getElementById("botCount").innerText = bots.length;

        bots.forEach(b => {
            let cls = b.joined ? "tag-on" : "tag-off";
            let txt = b.joined ? "ONLINE" : "WAIT";
            let div = document.createElement("div");
            div.className = "list-item";
            div.innerHTML = `<span style="color:#ddd">${b.user}</span> <span class="tag ${cls}">${txt}</span>`;
            box.appendChild(div);
        });
    }

    function updateUserList() {
        let box = document.getElementById("userList");
        box.innerHTML = "";
        document.getElementById("uCount").innerText = usersMap.size;

        usersMap.forEach((u) => {
            let name = u.name || u.username || "Unknown";
            let isMe = myBotNames.includes(name);
            let color = isMe ? "var(--primary)" : "#ccc";
            
            let icon = u.avatar_url || u.icon || "https://ui-avatars.com/api/?name="+name;
            if(!icon.startsWith("http")) icon = "https://chatp.net" + icon;

            let row = document.createElement("div");
            row.className = "list-item";
            row.onclick = () => lockTarget(name); // Tap to Spy
            
            row.innerHTML = `
                <div style="display:flex; align-items:center;">
                    <img src="${icon}" class="u-pic">
                    <span style="color:${color}">${name}</span>
                </div>
                <button class="btn-sm btn-cyan">SPY</button>
            `;
            box.appendChild(row);
        });
    }

    // --- SPY & COPYCAT LOGIC ---
    function lockTarget(name) {
        targetUser = name;
        document.getElementById("targetName").value = name;
        document.getElementById("targetStatus").innerText = "LOCKED";
        document.getElementById("targetStatus").style.color = "var(--secondary)";
        
        // Auto switch to Spy Tab
        let btns = document.querySelectorAll('.nav-btn');
        switchTab('tab3', btns[2]);
        
        // Reset View
        document.getElementById("spyFeed").innerHTML = "";
        spyLogs = [];
        sysLog(`Target Locked: ${name}`);
    }

    function toggleCopycat() {
        if(!targetUser) { alert("Select a target first!"); return; }
        isCopycat = !isCopycat;
        let btn = document.getElementById("btnCopycat");
        if(isCopycat) {
            btn.innerText = "🦜 COPYCAT ACTIVE";
            btn.classList.remove("btn-cyan"); btn.classList.add("btn-red");
            sysLog("Copycat Started");
        } else {
            btn.innerText = "🦜 START COPYCAT";
            btn.classList.remove("btn-red"); btn.classList.add("btn-cyan");
            sysLog("Copycat Stopped");
        }
    }

    function onTargetMessage(msg) {
        // 1. Update UI
        let box = document.getElementById("spyFeed");
        let time = new Date().toLocaleTimeString();
        let div = document.createElement("div");
        div.className = "spy-msg";
        div.innerHTML = `<div class="spy-time">${time}</div><div class="spy-text">${msg}</div>`;
        box.prepend(div);

        // 2. Save for Export
        spyLogs.push(`[${time}] ${targetUser}: ${msg}`);

        // 3. Trigger Copycat
        if(isCopycat && isConnected) {
            bots.forEach(b => { if(b.joined) b.sendMessage(msg); });
        }
    }

    function downloadSpyLogs() {
        if(spyLogs.length === 0) { alert("No logs captured yet!"); return; }
        // Fix for encoding
        let content = "--- NEXUS SPY LOGS ---\nTarget: " + targetUser + "\n\n" + spyLogs.join("\n");
        let blob = new Blob([content], { type: "text/plain;charset=utf-8" });
        let url = URL.createObjectURL(blob);
        let a = document.createElement("a");
        a.href = url;
        a.download = `spy_${targetUser}_${Date.now()}.txt`;
        a.click();
    }
    
    function clearSpyLogs() {
        spyLogs = [];
        document.getElementById("spyFeed").innerHTML = '<div style="text-align:center; color:#444; margin-top:50px;">History Cleared</div>';
    }

    // --- BOT CLASS ---
    const ASCII = ["(｡♥‿♥｡)", "ʕ•ᴥ•ʔ", "🔥", "❤️", "⚡"];

    class Bot {
        constructor(user, pass, room, isMaster) {
            this.user = user;
            this.pass = pass;
            this.room = room;
            this.ws = null;
            this.joined = false;
            this.isMaster = isMaster; // Only master listens for spy
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
                    updateBotUI();
                }

                // MASTER BOT INTELLIGENCE
                if(this.isMaster) {
                    // Roster Update
                    if((data.handler === "roster" || data.handler === "room_users") && data.users) {
                        data.users.forEach(u => usersMap.set(u.username, u));
                        updateUserList();
                    }
                    if(data.handler === "room_event" && data.type === "join") {
                        usersMap.set(data.username, data); updateUserList();
                    }
                    if(data.handler === "room_event" && data.type === "leave") {
                        usersMap.delete(data.username); updateUserList();
                    }

                    // SPY LISTENER
                    if(data.handler === "room_event" && data.type === "text") {
                        if(data.from === targetUser) {
                            onTargetMessage(data.body);
                        }
                    }
                }
            };

            this.ws.onclose = () => {
                this.joined = false;
                updateBotUI();
            };
        }

        send(json) {
            if(this.ws && this.ws.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(json));
        }

        sendMessage(txt) {
            if(!this.joined) return;
            this.send({
                handler: "room_message", id: genId(), room: this.room,
                type: "text", body: txt, url: "", length: ""
            });
        }
        
        disconnect() { if(this.ws) this.ws.close(); }
    }

    // --- MAIN CONTROLS ---
    function connectArmy() {
        if(isConnected) return;
        let room = document.getElementById("roomName").value;
        let raw = document.getElementById("accString").value;
        if(!raw.includes("#")) { alert("No Bots!"); return; }

        usersMap.clear(); myBotNames = []; bots = [];
        updateUserList();

        let list = raw.split("@").filter(s => s.includes("#"));
        
        list.forEach((s, i) => {
            let [u, p] = s.split("#");
            myBotNames.push(u.trim());
            let bot = new Bot(u.trim(), p.trim(), room, (i===0));
            bots.push(bot);
            setTimeout(() => bot.connect(), i * 600);
        });

        isConnected = true;
        updateBotUI();
    }

    function startSpam() {
        if(!isConnected) { alert("Connect First!"); return; }
        if(isSpamming) return;
        
        isSpamming = true;
        sysLog("Spam Started");
        let speed = parseInt(document.getElementById("spamSpeed").value);

        spamInterval = setInterval(() => {
            let mode = document.getElementById("msgMode").value;
            let txt = document.getElementById("customMsg").value || ".";
            let burst = parseInt(document.getElementById("burstCount").value);

            let msg = (mode === "ascii") ? ASCII[Math.floor(Math.random()*ASCII.length)] : txt;

            bots.forEach(b => {
                if(b.joined) {
                    for(let k=0; k<burst; k++) b.sendMessage(msg);
                }
            });
        }, speed);
    }

    function stopSpam() {
        isSpamming = false;
        clearInterval(spamInterval);
        sysLog("Spam Stopped");
    }

    function disconnectAll() {
        stopSpam();
        isConnected = false;
        bots.forEach(b => b.disconnect());
        bots = [];
        updateBotUI();
        sysLog("Disconnected All");
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
