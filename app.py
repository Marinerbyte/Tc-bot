from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS ULTIMATE</title>
    <style>
        body { background-color: #000; color: #00ff00; font-family: 'Courier New', monospace; padding: 10px; margin: 0; }
        
        .container { max-width: 100%; margin: auto; }
        .box { border: 1px solid #333; background: #080808; padding: 10px; margin-bottom: 10px; border-radius: 4px; }
        
        h2 { text-align: center; border-bottom: 2px solid #00ff00; padding-bottom: 5px; color: white; margin-top: 0; }
        h3 { border-bottom: 1px dashed #444; padding-bottom: 3px; color: #ccc; font-size: 13px; margin: 0 0 5px 0; }

        label { color: #888; font-size: 10px; font-weight: bold; display: block; margin-top: 8px; }
        input, textarea, select { 
            width: 100%; background: #111; color: #fff; border: 1px solid #444; 
            padding: 8px; margin-top: 2px; box-sizing: border-box; font-family: monospace; font-size: 11px;
        }
        textarea { height: 80px; color: yellow; border: 1px solid #666; }

        .btn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-top: 10px; }
        button { padding: 12px; font-weight: bold; cursor: pointer; border: none; border-radius: 2px; font-size: 11px; color: white; }
        
        .btn-connect { background: #00008b; width: 100%; margin-top: 10px; } 
        .btn-attack { background: #006400; } 
        .btn-stop { background: #8b0000; } 

        .scroll-box { height: 150px; overflow-y: scroll; background: #000; border: 1px solid #222; padding: 5px; font-size: 10px; }
        
        /* USER LIST STYLE */
        .user-row { display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #222; padding: 3px; }
        .user-pic { width: 20px; height: 20px; border-radius: 50%; border: 1px solid #333; }
        .user-name { color: #ddd; }
        .is-bot { color: lime; }

        /* LOGS STYLE */
        .log-line { border-bottom: 1px solid #111; padding: 1px; }
        .log-sys { color: #888; }
        .log-chat { color: cyan; } /* Chat messages */
        .log-err { color: red; }
        
        .status-bar { font-size: 10px; color: orange; margin-bottom: 5px; text-align: center; }
    </style>
</head>
<body>

<div class="container">
    <h2>⚡ NEXUS ULTIMATE ⚡</h2>

    <!-- STEP 1: SETUP -->
    <div class="box">
        <h3>1. CONFIGURATION</h3>
        <label>🎯 Room Name:</label>
        <input type="text" id="roomName" value="ملتقى🥂العرب">

        <label>💂 Bots (user#pass@...)</label>
        <textarea id="accString" placeholder="bot1#pass123@bot2#pass123@"></textarea>

        <button class="btn-connect" onclick="connectArmy()">🔌 CONNECT BOTS (LOGIN & JOIN)</button>
        <div id="connStatus" class="status-bar">Status: Idle</div>
    </div>

    <!-- STEP 2: ATTACK -->
    <div class="box">
        <h3>2. ACTION CENTER</h3>
        <div style="display:flex; gap:5px;">
            <div style="flex:1">
                <label>⚡ Speed (ms):</label>
                <input type="number" id="spamSpeed" value="2000">
            </div>
            <div style="flex:1">
                <label>🎭 Mode:</label>
                <select id="msgMode">
                    <option value="custom">Custom</option>
                    <option value="ascii">ASCII</option>
                </select>
            </div>
        </div>

        <label>💬 Message:</label>
        <input type="text" id="customMsg" placeholder="Hello Chat!">

        <div class="btn-grid">
            <button class="btn-attack" onclick="startAttack()">🔥 START ATTACK</button>
            <button class="btn-stop" onclick="stopAttack()">⏸️ PAUSE</button>
        </div>
        <button class="btn-stop" style="width:100%; margin-top:5px; background:#444;" onclick="disconnectAll()">❌ DISCONNECT ALL</button>
    </div>

    <!-- MONITOR -->
    <div class="box">
        <h3>👥 Room Users (<span id="uCount">0</span>)</h3>
        <div id="userList" class="scroll-box" style="height:120px;"></div>
    </div>

    <!-- CHAT FEED -->
    <div class="box">
        <h3>💬 Live Chat Feed</h3>
        <div id="logs" class="scroll-box"></div>
    </div>
</div>

<script>
    let bots = [];
    let isConnected = false;
    let isSpamming = false;
    let spamInterval = null;
    let usersMap = new Map();
    let myBotNames = [];

    // --- UTILS ---
    function log(msg, type="log-sys") {
        let box = document.getElementById("logs");
        let d = document.createElement("div");
        d.className = "log-line " + type;
        d.innerText = msg;
        box.prepend(d);
    }

    function status(msg) {
        document.getElementById("connStatus").innerText = msg;
    }

    function genId(len=20) {
        let c="abcdef0123456789", s="";
        for(let i=0; i<len; i++) s += c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    // --- UI RENDER ---
    function renderUsers() {
        let box = document.getElementById("userList");
        box.innerHTML = "";
        document.getElementById("uCount").innerText = usersMap.size;

        usersMap.forEach((u) => {
            let name = u.username || u.name || "Unknown"; // Fix parsing
            let isMyBot = myBotNames.includes(name);
            
            // Fix Avatar URL logic based on logs
            let icon = "https://ui-avatars.com/api/?name=" + name;
            // The logs don't show full avatar url in user list sometimes, so we default or fix if present
            
            let row = document.createElement("div");
            row.className = "user-row";
            let cls = isMyBot ? "is-bot" : "";
            
            row.innerHTML = `
                <img src="${icon}" class="user-pic"> 
                <span class="user-name ${cls}">${name}</span>
            `;
            box.appendChild(row);
        });
    }

    // --- BOT LOGIC ---
    const ASCII = ["(｡♥‿♥｡)", "ʕ•ᴥ•ʔ", "🔥", "❤️", "⚡", "🚀", "💀"];

    class Bot {
        constructor(user, pass, room) {
            this.user = user;
            this.pass = pass;
            this.room = room;
            this.ws = null;
            this.joined = false;
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
                
                // 2. JOINED (THIS IS WHERE USER LIST IS!)
                else if(data.handler === "room_event" && data.type === "you_joined") {
                    this.joined = true;
                    // FIX: Capture user list from 'users' array inside 'you_joined'
                    if(data.users && Array.isArray(data.users)) {
                        data.users.forEach(u => usersMap.set(u.username, u));
                        renderUsers();
                    }
                    log(`[SYS] ${this.user} Joined & Parsed List`, "log-sys");
                }

                // 3. OTHER USERS JOINING/LEAVING
                else if(data.handler === "room_event" && data.type === "join") {
                    let uName = data.username || data.name;
                    if(uName) {
                        usersMap.set(uName, {username: uName});
                        renderUsers();
                        log(`[JOIN] ${uName}`, "log-sys");
                    }
                }
                else if(data.handler === "room_event" && data.type === "leave") {
                    let uName = data.username || data.name;
                    if(uName) {
                        usersMap.delete(uName);
                        renderUsers();
                    }
                }

                // 4. CHAT MESSAGES (Confirm message sent)
                else if(data.handler === "room_event" && data.type === "text") {
                    log(`[CHAT] ${data.from}: ${data.body}`, "log-chat");
                }
            };

            this.ws.onclose = () => {
                this.joined = false;
                this.ws = null;
            };
        }

        send(json) {
            if(this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify(json));
            }
        }

        sendMessage(txt) {
            if(!this.joined) return;
            
            // METHOD A PAYLOAD (Proven Working)
            this.send({
                handler: "room_message",
                id: genId(),
                room: this.room,
                type: "text",
                body: txt,
                url: "",
                length: ""
            });
        }
        
        disconnect() {
            if(this.ws) this.ws.close();
        }
    }

    // --- CONTROLS ---
    function connectArmy() {
        if(isConnected) { alert("Already connected!"); return; }
        
        let room = document.getElementById("roomName").value;
        let raw = document.getElementById("accString").value;
        if(!raw.includes("#")) { alert("Enter Bots!"); return; }

        usersMap.clear();
        renderUsers();
        document.getElementById("logs").innerHTML = "";
        myBotNames = [];
        bots = [];

        let list = raw.split("@").filter(s => s.includes("#"));
        
        list.forEach((acc, i) => {
            let [u, p] = acc.split("#");
            let user = u.trim();
            myBotNames.push(user);
            
            let bot = new Bot(user, p.trim(), room);
            bots.push(bot);
            
            setTimeout(() => bot.connect(), i * 800);
        });

        isConnected = true;
        status(`Connecting ${list.length} bots...`);
    }

    function startAttack() {
        if(!isConnected) { alert("Connect first!"); return; }
        if(isSpamming) return;

        isSpamming = true;
        let speed = parseInt(document.getElementById("spamSpeed").value);
        log("🔥 ATTACK STARTED", "log-sys");

        spamInterval = setInterval(() => {
            if(!isSpamming) return;
            
            let mode = document.getElementById("msgMode").value;
            let txt = document.getElementById("customMsg").value || "Hello";

            bots.forEach(b => {
                if(b.joined) {
                    let msg = (mode === "ascii") ? ASCII[Math.floor(Math.random()*ASCII.length)] : txt;
                    b.sendMessage(msg);
                }
            });
        }, speed);
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
        status("Status: Disconnected");
        log("❌ DISCONNECTED", "log-err");
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
