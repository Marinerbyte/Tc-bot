from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Remanu Ultimate Command Center</title>
    <style>
        /* --- DARK THEME STYLING --- */
        body { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; margin: 0; padding: 10px; }
        
        /* LAYOUT GRID */
        .grid-container { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        @media (max-width: 768px) { .grid-container { grid-template-columns: 1fr; } }

        /* BOXES */
        .box { border: 1px solid #333; background: #111; padding: 10px; border-radius: 5px; }
        h3 { margin-top: 0; border-bottom: 1px solid #00ff41; padding-bottom: 5px; color: white; font-size: 14px; }

        /* INPUTS */
        label { color: #aaa; font-size: 11px; font-weight: bold; display: block; margin-top: 8px; }
        input, textarea, select { 
            width: 100%; background: #1a1a1a; color: #fff; border: 1px solid #444; 
            padding: 8px; margin-top: 3px; box-sizing: border-box; border-radius: 3px; font-size: 12px;
        }
        textarea { height: 100px; color: yellow; border: 1px solid #666; font-family: monospace; }

        /* BUTTONS */
        button { width: 100%; padding: 10px; font-weight: bold; cursor: pointer; border: none; margin-top: 10px; border-radius: 3px; }
        .btn-start { background: green; color: white; }
        .btn-stop { background: red; color: white; }

        /* LOGS & LISTS */
        .scroll-box { height: 200px; overflow-y: scroll; background: #000; border: 1px solid #333; padding: 5px; font-size: 10px; }
        
        /* BOT STATUS TABLE */
        .status-row { display: flex; justify-content: space-between; border-bottom: 1px solid #222; padding: 2px; }
        .st-online { color: #00ff00; }
        .st-fail { color: #ff0000; text-decoration: line-through; }
        .st-wait { color: #ffff00; }

        /* ROOM USER LIST */
        .user-item { display: flex; align-items: center; gap: 5px; border-bottom: 1px solid #222; padding: 2px; }
        .user-avatar { width: 20px; height: 20px; border-radius: 50%; border: 1px solid #555; }
        .user-name { color: white; }
        .user-role { font-size: 9px; color: #aaa; }

    </style>
</head>
<body>

<h2 style="text-align:center; margin:5px;">🤖 Remanu Command Center</h2>

<div class="grid-container">
    
    <!-- LEFT: CONTROLS -->
    <div class="box">
        <h3>🚀 Controls</h3>
        <label>🎯 Target Room:</label>
        <input type="text" id="roomName" value="ملتقى🥂العرب">
        
        <label>📝 Bots (user#pass@...)</label>
        <textarea id="accountString" placeholder="user#pass@user#pass@"></textarea>
        
        <div style="display:flex; gap:5px;">
            <div style="flex:1">
                <label>⏱️ Delay (s):</label>
                <input type="number" id="msgDelay" value="2">
            </div>
            <div style="flex:1">
                <label>🎭 Mode:</label>
                <select id="msgMode">
                    <option value="custom">✍️ Custom</option>
                    <option value="ascii">🎲 ASCII</option>
                    <option value="ghost">👻 Ghost</option>
                </select>
            </div>
        </div>

        <input type="text" id="customText" placeholder="Message content..." style="margin-top:5px;">

        <button class="btn-start" onclick="startBots()">LAUNCH SYSTEM</button>
        <button class="btn-stop" onclick="stopBots()">EMERGENCY STOP</button>
    </div>

    <!-- RIGHT: MONITORING -->
    <div class="box">
        <h3>📊 Live Bot Status</h3>
        <div id="botStatusList" class="scroll-box" style="height:100px;"></div>
        
        <h3 style="margin-top:10px;">👥 Room Users (<span id="userCount">0</span>)</h3>
        <div id="roomUserList" class="scroll-box" style="height:150px;"></div>
    </div>

</div>

<!-- LOGS AT BOTTOM -->
<div class="box" style="margin-top:10px;">
    <h3>📜 System Logs</h3>
    <div id="logs" class="scroll-box" style="height:120px;"></div>
</div>

<script>
    let activeSockets = [];
    let isRunning = false;
    let roomUserSet = new Set(); // To track unique users in room

    // --- UTILS ---
    function log(msg) {
        let box = document.getElementById("logs");
        let div = document.createElement("div");
        div.innerText = "> " + msg;
        box.prepend(div);
    }

    function updateBotStatus(user, status) {
        let box = document.getElementById("botStatusList");
        let existing = document.getElementById("st-" + user);
        
        let colorClass = "st-wait";
        if(status === "ONLINE") colorClass = "st-online";
        if(status === "FAILED") colorClass = "st-fail";

        let html = `<span class="${colorClass}">${user}</span> <span>[${status}]</span>`;

        if (existing) {
            existing.innerHTML = html;
        } else {
            let div = document.createElement("div");
            div.id = "st-" + user;
            div.className = "status-row";
            div.innerHTML = html;
            box.appendChild(div);
        }
    }

    // --- AUTO DELETE FAILED ID ---
    function removeFailedID(badUser) {
        let textarea = document.getElementById("accountString");
        let raw = textarea.value;
        
        // Logic to remove "user#pass@" or "user#pass"
        // Simple regex approach
        let regex = new RegExp(badUser + "#[^@]+@?", "g");
        let newVal = raw.replace(regex, "");
        
        textarea.value = newVal;
        log(`🗑️ Auto-Deleted Invalid ID: ${badUser}`);
    }

    // --- ROOM USER LIST ---
    function updateRoomList(usersArray) {
        let box = document.getElementById("roomUserList");
        box.innerHTML = ""; // Clear and rebuild (simple way)
        
        document.getElementById("userCount").innerText = usersArray.length;

        usersArray.forEach(u => {
            let name = u.username || u.name || "Unknown";
            let role = u.role || "Member";
            let icon = u.avatar_url || u.icon || u.image || "https://ui-avatars.com/api/?name="+name;
            if(!icon.startsWith("http")) icon = "https://chatp.net" + icon;

            let div = document.createElement("div");
            div.className = "user-item";
            div.innerHTML = `
                <img src="${icon}" class="user-avatar">
                <div>
                    <div class="user-name">${name}</div>
                    <div class="user-role">${role.toUpperCase()}</div>
                </div>
            `;
            box.appendChild(div);
        });
    }

    // --- BOT LOGIC ---
    const ASCII_LIB = ["(｡♥‿♥｡)", "ʕ•ᴥ•ʔ", "(ง'̀-'́)ง", "✨🌟✨", "🔥", "❤️"];

    function generateId(len=16) {
        let c = "abcdef0123456789", s = "";
        for(let i=0; i<len; i++) s += c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    class Bot {
        constructor(user, pass, room, delay, mode, customMsg) {
            this.user = user;
            this.pass = pass;
            this.room = room;
            this.delay = delay * 1000;
            this.mode = mode;
            this.customMsg = customMsg;
            this.ws = null;
            this.id = generateId();
        }

        connect() {
            if (!isRunning) return;
            updateBotStatus(this.user, "CONNECTING...");
            
            this.ws = new WebSocket("wss://chatp.net:5333/server");

            this.ws.onopen = () => {
                this.send({ handler: "login", id: this.id, username: this.user, password: this.pass });
            };

            this.ws.onmessage = (e) => {
                let data = JSON.parse(e.data);

                // 1. LOGIN SUCCESS
                if (data.handler === "login_event" && data.type === "success") {
                    updateBotStatus(this.user, "LOGGED IN");
                    this.send({ handler: "room_join", id: generateId(), name: this.room });
                }
                
                // 1.1 LOGIN FAILED (CRITICAL)
                else if (data.handler === "login_event" && data.type === "error") {
                    updateBotStatus(this.user, "FAILED");
                    removeFailedID(this.user); // Auto Delete
                    this.ws.close();
                }

                // 2. ROOM JOINED
                else if (data.handler === "room_event" && data.type === "room_joined") {
                    updateBotStatus(this.user, "ONLINE");
                    
                    if (this.mode !== "ghost") {
                        let msg = (this.mode === "ascii") ? ASCII_LIB[Math.floor(Math.random()*ASCII_LIB.length)] : (this.customMsg || "Hello");
                        setTimeout(() => {
                            if(isRunning) this.send({ handler: "room_message", id: generateId(), room: this.room, type: "text", body: msg });
                        }, this.delay);
                    }
                }

                // 3. CAPTURE USER LIST (ROSTER)
                // Chatp sends 'roster' handler with 'users' array
                else if (data.handler === "roster") {
                    if (data.users && data.users.length > 0) {
                        updateRoomList(data.users);
                    }
                }
            };

            this.ws.onclose = () => updateBotStatus(this.user, "DISCONNECTED");
            this.ws.onerror = () => {
                updateBotStatus(this.user, "FAILED");
                // Optional: removeFailedID(this.user); // Uncomment if connection error should also delete ID
            };
            
            activeSockets.push(this.ws);
        }

        send(json) {
            if (this.ws.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(json));
        }
    }

    function startBots() {
        if (isRunning) return;
        let room = document.getElementById("roomName").value;
        let rawString = document.getElementById("accountString").value;
        let delayVal = document.getElementById("msgDelay").value;
        let mode = document.getElementById("msgMode").value;
        let customMsg = document.getElementById("customText").value;

        if (!rawString.includes("#") || !rawString.includes("@")) { alert("Format: user#pass@"); return; }

        isRunning = true;
        document.getElementById("botStatusList").innerHTML = ""; // Clear Status List

        let accounts = rawString.split("@");
        let validBots = [];
        accounts.forEach(acc => {
            if (acc.includes("#")) {
                let p = acc.split("#");
                if(p[0] && p[1]) validBots.push({u: p[0].trim(), p: p[1].trim()});
            }
        });

        log(`[*] Launching ${validBots.length} Bots...`);

        validBots.forEach((botData, index) => {
            setTimeout(() => {
                if (!isRunning) return;
                let bot = new Bot(botData.u, botData.p, room, delayVal, mode, customMsg);
                bot.connect();
            }, index * 800);
        });
    }

    function stopBots() {
        isRunning = false;
        log("🛑 Stopping All...");
        activeSockets.forEach(s => s.close());
        activeSockets = [];
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
