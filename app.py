from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS PRIME</title>
    <style>
        /* --- DARK THEME --- */
        body { background-color: #000; color: #00ff00; font-family: 'Courier New', monospace; margin: 0; padding: 5px; height: 100vh; display: flex; flex-direction: column; }
        
        /* LAYOUT */
        .main { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; flex: 1; overflow: hidden; }
        @media (max-width: 600px) { .main { grid-template-columns: 1fr; } }

        .panel { border: 1px solid #333; background: #080808; padding: 5px; display: flex; flex-direction: column; }
        
        /* INPUTS */
        label { color: #888; font-size: 10px; font-weight: bold; display: block; margin-top: 5px; }
        input, textarea, select { 
            width: 100%; background: #111; color: #fff; border: 1px solid #444; 
            padding: 5px; margin-top: 2px; box-sizing: border-box; font-size: 11px;
        }
        textarea { height: 60px; color: yellow; }

        /* BUTTONS */
        .btn-group { display: flex; gap: 5px; margin-top: 10px; }
        button { flex: 1; padding: 10px; font-weight: bold; cursor: pointer; border: none; border-radius: 3px; font-size: 11px; }
        .btn-go { background: green; color: white; }
        .btn-stop { background: red; color: white; }

        /* MONITORING */
        .scroll { overflow-y: scroll; background: #000; border: 1px solid #222; padding: 5px; flex: 1; font-size: 10px; }
        .user-row { display: flex; align-items: center; gap: 5px; border-bottom: 1px solid #222; padding: 2px; }
        .user-pic { width: 18px; height: 18px; border-radius: 50%; }
        
        /* LOGS */
        .log-entry { border-bottom: 1px solid #111; padding: 1px; }
        .sent { color: cyan; }
        .err { color: red; }
    </style>
</head>
<body>

<h3 style="text-align:center; margin:5px; border-bottom:1px solid lime;">🤖 NEXUS PRIME</h3>

<div class="main">
    <!-- LEFT: CONTROLS -->
    <div class="panel">
        <label>🎯 Room Name</label>
        <input type="text" id="roomName" value="ملتقى🥂العرب">

        <label>📝 Bots (user#pass@...)</label>
        <textarea id="accString" placeholder="bot1#pass123@bot2#pass123@"></textarea>

        <!-- TIMERS RESTORED -->
        <div style="display:flex; gap:5px;">
            <div style="flex:1">
                <label>⏳ Start In (s):</label>
                <input type="number" id="startDelay" value="2">
            </div>
            <div style="flex:1">
                <label>⏱️ Run For (s):</label>
                <input type="number" id="duration" value="60">
            </div>
        </div>

        <div style="display:flex; gap:5px;">
            <div style="flex:1">
                <label>⚡ Speed (ms):</label>
                <input type="number" id="speed" value="2000">
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
        <input type="text" id="customMsg" placeholder="Hello">

        <div class="btn-group">
            <button class="btn-go" onclick="startMission()">🚀 START</button>
            <button class="btn-stop" onclick="stopMission()">🛑 STOP</button>
        </div>
        
        <div id="statusBox" style="margin-top:5px; font-size:10px; color:orange;">Ready.</div>
    </div>

    <!-- RIGHT: MONITOR -->
    <div class="panel">
        <div style="font-size:10px; color:#aaa;">👥 USERS IN ROOM: <span id="uCount" style="color:white;">0</span></div>
        <div id="userList" class="scroll" style="height:100px;"></div>
        
        <div style="font-size:10px; color:#aaa; margin-top:5px;">📜 LIVE LOGS:</div>
        <div id="logs" class="scroll"></div>
    </div>
</div>

<script>
    let activeBots = [];
    let isRunning = false;
    let spamTimer = null;
    let stopTimer = null;
    let usersMap = new Map();

    // --- UTILS ---
    function log(msg, type="") {
        let box = document.getElementById("logs");
        let d = document.createElement("div");
        d.className = "log-entry " + type;
        d.innerText = "> " + msg;
        box.prepend(d);
    }

    function status(msg) {
        document.getElementById("statusBox").innerText = msg;
    }

    function genId(len=18) {
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
            let icon = u.avatar_url || u.icon || "https://ui-avatars.com/api/?name="+name;
            if(!icon.startsWith("http")) icon = "https://chatp.net" + icon;
            
            let d = document.createElement("div");
            d.className = "user-row";
            d.innerHTML = `<img src="${icon}" class="user-pic"> <span>${name}</span>`;
            box.appendChild(d);
        });
    }

    // --- BOT LOGIC ---
    const ASCII = ["(｡♥‿♥｡)", "ʕ•ᴥ•ʔ", "🔥", "❤️", "⚡", "🚀", "✨"];

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
            
            this.ws = new WebSocket("wss://chatp.net:5333/server");

            this.ws.onopen = () => {
                // LOGIN
                this.send({ handler: "login", id: genId(), username: this.user, password: this.pass });
            };

            this.ws.onmessage = (e) => {
                let data = JSON.parse(e.data);

                // 1. LOGIN OK -> JOIN
                if(data.handler === "login_event" && data.type === "success") {
                    this.send({ handler: "room_join", id: genId(), name: this.room });
                }
                
                // 2. JOINED -> READY
                else if(data.handler === "room_event" && data.type === "room_joined") {
                    this.joined = true;
                    log(`${this.user} Joined!`);
                }

                // 3. CAPTURE USERS
                else if(data.handler === "roster") {
                    if(data.users) {
                        data.users.forEach(u => usersMap.set(u.id || u.user_id, u));
                        renderUsers();
                    }
                }
                else if(data.handler === "room_event" && data.type === "join") {
                    usersMap.set(data.id || data.user_id, data);
                    renderUsers();
                }
            };

            this.ws.onclose = () => {
                this.joined = false;
                if(isRunning) log(`${this.user} Disconnected`, "err");
            };
        }

        send(json) {
            if(this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify(json));
            }
        }

        sendMessage(txt) {
            if(!this.joined) return;
            
            // --- FIXED PAYLOAD (Based on tanvar.py) ---
            this.send({
                handler: "room_message",
                id: genId(),       // Unique ID every time
                room: this.room,
                type: "text",      // Type text
                body: txt,
                url: "",           // Empty String (Important)
                length: ""         // Empty String (Critical Fix)
            });
            log(`${this.user} -> Sent`, "sent");
        }
    }

    // --- MAIN CONTROLLER ---
    function startMission() {
        if(isRunning) return;
        
        let raw = document.getElementById("accString").value;
        let room = document.getElementById("roomName").value;
        if(!raw.includes("#")) { alert("No Accounts!"); return; }

        isRunning = true;
        usersMap.clear();
        renderUsers();
        document.getElementById("logs").innerHTML = "";
        
        // 1. Launch Bots
        let list = raw.split("@").filter(s => s.includes("#"));
        activeBots = list.map(s => {
            let [u, p] = s.split("#");
            return new Bot(u.trim(), p.trim(), room);
        });

        status(`Connecting ${activeBots.length} bots...`);
        activeBots.forEach((b, i) => setTimeout(() => { if(isRunning) b.connect(); }, i*300));

        // 2. Schedule Spam Start
        let startDelay = document.getElementById("startDelay").value * 1000;
        let speed = document.getElementById("speed").value;
        
        status(`Waiting ${startDelay/1000}s to start messaging...`);

        setTimeout(() => {
            if(!isRunning) return;
            status("🔥 SPAMMING ACTIVE 🔥");
            log("--- STARTING MESSAGES ---");

            spamInterval = setInterval(() => {
                if(!isRunning) return;
                
                let mode = document.getElementById("msgMode").value;
                let txt = document.getElementById("customMsg").value || ".";
                
                activeBots.forEach(b => {
                    if(b.joined) {
                        let msg = (mode === "ascii") ? ASCII[Math.floor(Math.random()*ASCII.length)] : txt;
                        b.sendMessage(msg);
                    }
                });
            }, speed);

        }, startDelay);

        // 3. Schedule Auto Stop
        let duration = document.getElementById("duration").value * 1000;
        stopTimer = setTimeout(() => {
            log("⏳ Time Limit Reached.");
            stopMission();
        }, duration + startDelay);
    }

    function stopMission() {
        isRunning = false;
        clearInterval(spamInterval);
        clearTimeout(stopTimer);
        status("🛑 STOPPED");
        activeBots.forEach(b => { if(b.ws) b.ws.close(); });
        activeBots = [];
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
