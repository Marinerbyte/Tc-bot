from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS CONTROLLER</title>
    <style>
        body { background-color: #000; color: #00ff00; font-family: 'Courier New', monospace; padding: 10px; margin: 0; }
        
        /* LAYOUT */
        .container { max-width: 100%; margin: auto; }
        .box { border: 1px solid #333; background: #080808; padding: 10px; margin-bottom: 10px; border-radius: 4px; }
        
        h2 { text-align: center; border-bottom: 1px solid #00ff00; padding-bottom: 5px; color: white; margin-top: 0; }
        h3 { font-size: 14px; border-bottom: 1px dashed #444; padding-bottom: 3px; margin: 0 0 5px 0; color: #ccc; }

        /* INPUTS */
        label { font-size: 11px; font-weight: bold; color: #666; display: block; margin-top: 5px; }
        input, textarea, select { 
            width: 100%; background: #111; color: #fff; border: 1px solid #444; 
            padding: 8px; margin-top: 2px; box-sizing: border-box; font-family: monospace;
        }
        textarea { height: 80px; color: yellow; font-size: 11px; border: 1px solid #666; }

        /* BUTTONS */
        button { width: 100%; padding: 12px; font-weight: bold; cursor: pointer; border: none; margin-top: 10px; border-radius: 2px; }
        .btn-start { background: #006400; color: white; }
        .btn-stop { background: #8b0000; color: white; }

        /* LOGS & STATUS */
        .scroll-box { height: 150px; overflow-y: scroll; background: #000; border: 1px solid #222; padding: 5px; font-size: 10px; }
        .log-line { border-bottom: 1px solid #111; padding: 1px; }

        /* BOT STATUS GRID */
        .bot-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; max-height: 100px; overflow-y: auto; }
        .bot-card { background: #111; padding: 3px; border: 1px solid #333; font-size: 10px; display: flex; justify-content: space-between; }
        .st-con { color: yellow; }
        .st-on { color: lime; font-weight: bold; }
        .st-dead { color: red; text-decoration: line-through; }

        /* USER LIST */
        .user-row { display: flex; align-items: center; gap: 5px; border-bottom: 1px solid #222; padding: 2px; }
        .user-pfp { width: 20px; height: 20px; border-radius: 50%; background: #333; }
    </style>
</head>
<body>

<div class="container">
    <h2>NEXUS CONTROLLER</h2>

    <!-- CONTROLS -->
    <div class="box">
        <h3>🚀 Mission Control</h3>
        <label>🎯 Room Name:</label>
        <input type="text" id="roomName" value="ملتقى🥂العرب">

        <label>💂 Bots (user#pass@...)</label>
        <textarea id="accString" placeholder="bot1#pass123@bot2#pass123@"></textarea>

        <div style="display:flex; gap:5px;">
            <div style="flex:1">
                <label>⏱️ Delay (Sec):</label>
                <input type="number" id="startDelay" value="2">
            </div>
            <div style="flex:1">
                <label>⚡ Speed (ms):</label>
                <input type="number" id="spamSpeed" value="2000">
            </div>
        </div>

        <div style="display:flex; gap:5px;">
            <div style="flex:1">
                <label>⌛ Stop After (s):</label>
                <input type="number" id="duration" value="60">
            </div>
            <div style="flex:1">
                <label>🎭 Message Type:</label>
                <select id="msgMode">
                    <option value="custom">✍️ Custom</option>
                    <option value="ascii">🧸 ASCII</option>
                </select>
            </div>
        </div>

        <label>💬 Message Text:</label>
        <input type="text" id="msgText" placeholder="Hello Chat!">

        <button class="btn-start" onclick="launchAttack()">🚀 START MISSION</button>
        <button class="btn-stop" onclick="abortMission()">🛑 ABORT MISSION</button>
    </div>

    <!-- MONITORING -->
    <div class="box">
        <h3>📡 Status Monitor</h3>
        <div id="botGrid" class="bot-grid"></div>
        
        <h3 style="margin-top:10px;">👥 Room Users (<span id="uCount">0</span>)</h3>
        <div id="userList" class="scroll-box"></div>
    </div>

    <!-- LOGS -->
    <div class="box">
        <h3>📜 Event Logs</h3>
        <div id="logs" class="scroll-box"></div>
    </div>
</div>

<script>
    let activeBots = [];
    let isRunning = false;
    let globalInterval = null;
    let usersMap = new Map();

    // --- LOGGING ---
    function log(msg) {
        let box = document.getElementById("logs");
        let div = document.createElement("div");
        div.className = "log-line";
        div.innerText = "> " + msg;
        box.prepend(div);
    }

    // --- UI UPDATES ---
    function updateBotUI(user, status) {
        let grid = document.getElementById("botGrid");
        let card = document.getElementById("b-" + user);
        
        let cls = "st-con";
        if(status === "ONLINE") cls = "st-on";
        if(status === "FAILED") cls = "st-dead";

        let html = `<span>${user}</span> <span class="${cls}">${status}</span>`;

        if(card) {
            card.innerHTML = html;
        } else {
            let div = document.createElement("div");
            div.id = "b-" + user;
            div.className = "bot-card";
            div.innerHTML = html;
            grid.appendChild(div);
        }
    }

    function renderUsers() {
        let box = document.getElementById("userList");
        box.innerHTML = "";
        document.getElementById("uCount").innerText = usersMap.size;

        usersMap.forEach((u, id) => {
            let name = u.name || u.username || "Unknown";
            let icon = u.icon || u.avatar_url || "https://ui-avatars.com/api/?name="+name;
            if(!icon.startsWith("http")) icon = "https://chatp.net" + icon;
            
            let row = document.createElement("div");
            row.className = "user-row";
            row.innerHTML = `<img src="${icon}" class="user-pfp"> <span>${name}</span>`;
            box.appendChild(row);
        });
    }

    function generateId(len=16) {
        let c="abcdef0123456789", s="";
        for(let i=0; i<len; i++) s += c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    // --- ASCII LIBRARY ---
    const ASCII = ["(｡♥‿♥｡)", "ʕ•ᴥ•ʔ", "✨🌟✨", "🔥", "❤️", "(ง'̀-'́)ง", "🚀", "⚡", "UwU", "OwO"];

    // --- BOT CLASS ---
    class Bot {
        constructor(user, pass, room) {
            this.user = user;
            this.pass = pass;
            this.room = room;
            this.ws = null;
            this.joined = false;
        }

        connect() {
            if(!isRunning) return;
            updateBotUI(this.user, "Wait...");
            
            this.ws = new WebSocket("wss://chatp.net:5333/server");

            this.ws.onopen = () => {
                this.send({ handler: "login", id: generateId(), username: this.user, password: this.pass });
            };

            this.ws.onmessage = (e) => {
                let data = JSON.parse(e.data);

                // DEBUG LOG (To see what server sends)
                if(data.handler === "roster") console.log("ROSTER RECEIVED", data);

                // 1. LOGIN SUCCESS
                if(data.handler === "login_event" && data.type === "success") {
                    this.send({ handler: "room_join", id: generateId(), name: this.room });
                }
                
                // 1.1 LOGIN FAIL
                else if(data.handler === "login_event" && data.type === "error") {
                    updateBotUI(this.user, "FAILED");
                    this.ws.close();
                }

                // 2. ROOM JOINED
                else if(data.handler === "room_event" && data.type === "room_joined") {
                    this.joined = true;
                    updateBotUI(this.user, "ONLINE");
                }

                // 3. USER LIST HANDLING (ROSTER)
                else if(data.handler === "roster") {
                    if(data.users) {
                        data.users.forEach(u => usersMap.set(u.id || u.user_id, u));
                        renderUsers();
                    }
                }
                // LIVE JOIN/LEAVE
                else if(data.handler === "room_event" && data.type === "join") {
                    usersMap.set(data.id || data.user_id, data);
                    renderUsers();
                }
                else if(data.handler === "room_event" && data.type === "leave") {
                    usersMap.delete(data.id || data.user_id);
                    renderUsers();
                }
            };

            this.ws.onclose = () => {
                this.joined = false;
                updateBotUI(this.user, "OFF");
            };
        }

        send(json) {
            if(this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify(json));
            }
        }

        sendMessage(text) {
            if(this.joined) {
                this.send({ 
                    handler: "room_message", 
                    id: generateId(), 
                    room: this.room, 
                    type: "text", 
                    body: text 
                });
            }
        }
    }

    // --- SYSTEM LOGIC ---
    function launchAttack() {
        if(isRunning) return;
        
        let raw = document.getElementById("accString").value;
        let room = document.getElementById("roomName").value;
        if(!raw.includes("#")) { alert("Enter Bots!"); return; }

        isRunning = true;
        usersMap.clear();
        renderUsers();
        document.getElementById("botGrid").innerHTML = "";

        // Parse Bots
        let list = raw.split("@").filter(s => s.includes("#"));
        activeBots = list.map(s => {
            let [u, p] = s.split("#");
            return new Bot(u.trim(), p.trim(), room);
        });

        log(`[*] Initiating ${activeBots.length} Bots...`);

        // Connect Staggered
        activeBots.forEach((bot, i) => {
            setTimeout(() => { if(isRunning) bot.connect(); }, i * 500);
        });

        // --- GLOBAL SPAM LOOPER (THE FIX) ---
        // Instead of relying on individual bot timers, we run ONE main loop
        let startDelay = parseInt(document.getElementById("startDelay").value) * 1000;
        let speed = parseInt(document.getElementById("spamSpeed").value);
        let mode = document.getElementById("msgMode").value;
        let txt = document.getElementById("msgText").value;

        // Start Spamming after delay
        setTimeout(() => {
            if(!isRunning) return;
            log("🔥 ATTACK STARTED (Global Loop Active)");
            
            globalInterval = setInterval(() => {
                if(!isRunning) return;
                
                // Pick a message
                let msg = (mode === "ascii") ? ASCII[Math.floor(Math.random()*ASCII.length)] : txt;
                if(!msg) msg = ".";

                // Force ALL joined bots to send
                activeBots.forEach(bot => {
                    if(bot.joined) bot.sendMessage(msg);
                });

            }, speed);

        }, startDelay);

        // Auto Stop
        let duration = parseInt(document.getElementById("duration").value) * 1000;
        setTimeout(() => abortMission, duration + startDelay);
    }

    function abortMission() {
        isRunning = false;
        clearInterval(globalInterval);
        activeBots.forEach(b => { if(b.ws) b.ws.close(); });
        log("🛑 MISSION ABORTED.");
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
