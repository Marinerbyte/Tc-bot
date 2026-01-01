from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS COMMANDER</title>
    <style>
        /* HACKER THEME */
        body { background-color: #050505; color: #00ff00; font-family: 'Consolas', monospace; margin: 0; padding: 10px; }
        
        .container { max-width: 100%; margin: auto; }
        .panel { border: 1px solid #333; background: #0a0a0a; padding: 10px; margin-bottom: 10px; border-radius: 4px; }
        
        h2 { text-align: center; border-bottom: 2px solid #00ff00; padding-bottom: 5px; color: white; margin-top: 0; text-transform: uppercase; letter-spacing: 2px; }
        h3 { border-bottom: 1px dashed #444; padding-bottom: 3px; color: #ccc; font-size: 14px; margin-top: 0; }

        /* CONTROLS */
        label { color: #888; font-size: 10px; font-weight: bold; display: block; margin-top: 8px; }
        input, textarea, select { 
            width: 100%; background: #111; color: #fff; border: 1px solid #444; 
            padding: 8px; margin-top: 2px; box-sizing: border-box; font-family: monospace; font-size: 11px;
        }
        textarea { height: 80px; color: yellow; border: 1px solid #666; }

        /* BUTTONS */
        .btn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-top: 10px; }
        button { padding: 12px; font-weight: bold; cursor: pointer; border: none; border-radius: 2px; font-size: 11px; color: white; }
        
        .btn-connect { background: #00008b; width: 100%; margin-top: 10px; } /* Blue */
        .btn-attack { background: #006400; } /* Green */
        .btn-stop { background: #8b0000; } /* Red */

        /* MONITORING */
        .scroll-box { height: 150px; overflow-y: scroll; background: #000; border: 1px solid #222; padding: 5px; font-size: 10px; }
        
        /* USER LIST */
        .user-row { display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #222; padding: 3px; }
        .user-pic { width: 22px; height: 22px; border-radius: 50%; border: 1px solid #333; }
        .user-name { color: #ddd; }
        .bot-tag { color: lime; font-size: 8px; border: 1px solid lime; padding: 0 2px; border-radius: 2px; }

        /* LOGS */
        .log-line { border-bottom: 1px solid #111; padding: 1px; }
        .log-in { color: yellow; }
        .log-out { color: cyan; }
        .log-sys { color: #888; }
    </style>
</head>
<body>

<div class="container">
    <h2>⚔️ NEXUS COMMANDER ⚔️</h2>

    <!-- STEP 1: CONNECTION -->
    <div class="panel">
        <h3>1. CONNECTION</h3>
        <label>🎯 Room Name:</label>
        <input type="text" id="roomName" value="ملتقى🥂العرب">

        <label>💂 Bots (user#pass@...)</label>
        <textarea id="accString" placeholder="bot1#pass123@bot2#pass123@"></textarea>

        <button class="btn-connect" onclick="connectArmy()">🔌 CONNECT ARMY (LOGIN ONLY)</button>
    </div>

    <!-- STEP 2: ATTACK -->
    <div class="panel">
        <h3>2. ACTION</h3>
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
            <button class="btn-attack" onclick="startAttack()">🔥 START SPAM</button>
            <button class="btn-stop" onclick="stopAttack()">⏸️ PAUSE SPAM</button>
        </div>
        
        <button class="btn-stop" style="width:100%; margin-top:5px; background: #444;" onclick="disconnectAll()">❌ DISCONNECT ALL</button>
    </div>

    <!-- MONITOR -->
    <div class="panel">
        <h3>👥 Room Users (<span id="uCount">0</span>)</h3>
        <div id="userList" class="scroll-box" style="height:120px;"></div>
    </div>

    <!-- LOGS -->
    <div class="panel">
        <h3>📜 Live Logs</h3>
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
        d.innerText = "> " + msg;
        box.prepend(d);
    }

    // ID Generator (20 chars like tanvar.py)
    function genId(len=20) {
        let c="abcdef0123456789", s="";
        for(let i=0; i<len; i++) s += c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    // --- USER LIST UI ---
    function renderUsers() {
        let box = document.getElementById("userList");
        box.innerHTML = "";
        document.getElementById("uCount").innerText = usersMap.size;

        usersMap.forEach((u) => {
            let name = u.name || u.username || "Unknown";
            let isMyBot = myBotNames.includes(name);
            
            // Avatar Fix
            let icon = u.avatar_url || u.icon || "https://ui-avatars.com/api/?name="+name;
            if(icon && !icon.startsWith("http")) icon = "https://chatp.net" + icon;

            let row = document.createElement("div");
            row.className = "user-row";
            
            let tag = isMyBot ? '<span class="bot-tag">BOT</span>' : '';
            
            row.innerHTML = `
                <img src="${icon}" class="user-pic"> 
                <span class="user-name" style="color:${isMyBot ? 'lime':'#ccc'}">${name} ${tag}</span>
            `;
            box.appendChild(row);
        });
    }

    // --- BOT CLASS ---
    const ASCII = ["(｡♥‿♥｡)", "ʕ•ᴥ•ʔ", "✨", "🔥", "❤️", "🚀", "⚡"];

    class Bot {
        constructor(user, pass, room) {
            this.user = user;
            this.pass = pass;
            this.room = room;
            this.ws = null;
            this.joined = false;
        }

        connect() {
            if(this.ws) return; // Already connected
            
            this.ws = new WebSocket("wss://chatp.net:5333/server");

            this.ws.onopen = () => {
                log(`${this.user}: Socket Open. Logging in...`);
                // Login
                this.send({ handler: "login", id: genId(), username: this.user, password: this.pass });
            };

            this.ws.onmessage = (e) => {
                let data = JSON.parse(e.data);

                // 1. LOGIN SUCCESS -> JOIN ROOM
                if(data.handler === "login_event" && data.type === "success") {
                    log(`${this.user}: Login OK. Joining...`, "log-in");
                    this.send({ handler: "room_join", id: genId(), name: this.room });
                }
                
                // 1.1 LOGIN FAIL
                else if(data.handler === "login_event" && data.type === "error") {
                    log(`${this.user}: Login FAILED!`, "log-out");
                    this.ws.close();
                }

                // 2. JOINED ROOM (READY)
                else if(data.handler === "room_event" && data.type === "room_joined") {
                    this.joined = true;
                    log(`${this.user}: Joined Room! Waiting for command.`, "log-in");
                }

                // 3. CAPTURE USERS (ROSTER)
                else if(data.handler === "roster") {
                    if(data.users) {
                        data.users.forEach(u => usersMap.set(u.id || u.user_id, u));
                        renderUsers();
                    }
                }
                // LIVE JOIN
                else if(data.handler === "room_event" && data.type === "join") {
                    usersMap.set(data.id || data.user_id, data);
                    renderUsers();
                }
                // LIVE LEAVE
                else if(data.handler === "room_event" && data.type === "leave") {
                    usersMap.delete(data.id || data.user_id);
                    renderUsers();
                }
            };

            this.ws.onclose = () => {
                this.joined = false;
                this.ws = null;
                log(`${this.user}: Disconnected`, "log-out");
            };
        }

        send(json) {
            if(this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify(json));
            }
        }

        sendMessage(txt) {
            if(!this.joined) return;
            
            // --- STRICT PAYLOAD (Matching tanvar.py exactly) ---
            this.send({
                handler: "room_message",
                id: genId(),       // 20 chars
                room: this.room,
                type: "text",
                body: txt,
                url: "",
                length: ""         // Empty String
            });
        }
        
        disconnect() {
            if(this.ws) this.ws.close();
        }
    }

    // --- CONTROLLER FUNCTIONS ---

    function connectArmy() {
        if(isConnected) { alert("Already Connected!"); return; }
        
        let room = document.getElementById("roomName").value;
        let raw = document.getElementById("accString").value;
        if(!raw.includes("#")) { alert("No Bots Found!"); return; }

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
            
            // Stagger connections (0.5s gap)
            setTimeout(() => bot.connect(), i * 500);
        });

        isConnected = true;
        log(`[*] Connecting ${list.length} bots...`);
    }

    function startAttack() {
        if(!isConnected) { alert("Connect Army First!"); return; }
        if(isSpamming) return;

        isSpamming = true;
        let speed = parseInt(document.getElementById("spamSpeed").value);
        log("🔥 ATTACK STARTED!", "log-in");

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
        log("⏸️ ATTACK PAUSED.", "log-sys");
    }

    function disconnectAll() {
        stopAttack();
        isConnected = false;
        bots.forEach(b => b.disconnect());
        bots = [];
        log("❌ ALL DISCONNECTED.", "log-out");
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
