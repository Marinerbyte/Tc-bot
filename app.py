from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Remanu Ultimate Controller</title>
    <style>
        body { background-color: #050505; color: #00ff41; font-family: monospace; padding: 10px; margin: 0; }
        
        /* LAYOUT */
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        @media (max-width: 700px) { .grid { grid-template-columns: 1fr; } }

        .box { border: 1px solid #333; background: #111; padding: 10px; border-radius: 5px; }
        h3 { border-bottom: 1px solid #00ff41; padding-bottom: 5px; margin-top: 0; color: white; font-size: 14px; }

        /* INPUTS */
        label { color: #ccc; font-size: 11px; font-weight: bold; display: block; margin-top: 8px; }
        input, textarea, select { 
            width: 100%; background: #222; color: #fff; border: 1px solid #555; 
            padding: 8px; margin-top: 3px; box-sizing: border-box; border-radius: 3px;
        }
        textarea { height: 100px; color: yellow; border: 1px solid #777; }
        #customText { border: 1px solid #00ff00; }

        /* BUTTONS */
        button { width: 100%; padding: 12px; font-weight: bold; cursor: pointer; border: none; margin-top: 10px; border-radius: 3px; }
        .btn-start { background: green; color: white; }
        .btn-stop { background: red; color: white; }
        .btn-force { background: orange; color: black; margin-top: 5px; }

        /* STATUS & LISTS */
        .scroll-box { height: 150px; overflow-y: scroll; background: #000; border: 1px solid #333; padding: 5px; font-size: 10px; }
        .status-row { display: flex; justify-content: space-between; border-bottom: 1px solid #222; padding: 2px; }
        .st-online { color: #00ff00; }
        .st-fail { color: #ff0000; text-decoration: line-through; }
        
        /* USER LIST */
        .user-item { display: flex; align-items: center; gap: 5px; border-bottom: 1px solid #222; padding: 2px; }
        .user-avatar { width: 20px; height: 20px; border-radius: 50%; }
    </style>
</head>
<body>

<h2 style="text-align:center; margin:5px; color:white;">🤖 Remanu Master Panel</h2>

<div class="grid">
    
    <!-- LEFT PANEL: SETTINGS -->
    <div class="box">
        <h3>🚀 Configuration</h3>
        <label>🎯 Target Room:</label>
        <input type="text" id="roomName" value="ملتقى🥂العرب">
        
        <label>📝 Accounts (user#pass@...)</label>
        <textarea id="accountString" placeholder="user#pass@user#pass@"></textarea>
        
        <div style="display:flex; gap:5px;">
            <div style="flex:1">
                <label>⏱️ Wait (Sec):</label>
                <input type="number" id="msgDelay" value="2">
            </div>
            <div style="flex:1">
                <label>🎭 Mode:</label>
                <select id="msgMode">
                    <option value="custom">✍️ Custom Text</option>
                    <option value="ascii">🎲 Random ASCII</option>
                    <option value="ghost">👻 Ghost (Silent)</option>
                </select>
            </div>
        </div>

        <label>💬 Message Content:</label>
        <input type="text" id="customText" placeholder="Type hello here...">

        <button class="btn-start" onclick="startBots()">🚀 LAUNCH & AUTO-MSG</button>
        <button class="btn-force" onclick="forceSend()">🔊 SEND MESSAGE NOW (MANUAL)</button>
        <button class="btn-stop" onclick="stopBots()">🛑 STOP ALL</button>
    </div>

    <!-- RIGHT PANEL: MONITOR -->
    <div class="box">
        <h3>📊 Bot Status</h3>
        <div id="botStatusList" class="scroll-box" style="height:120px;"></div>
        
        <h3 style="margin-top:10px;">👥 Room Users (<span id="userCount">0</span>)</h3>
        <div id="roomUserList" class="scroll-box"></div>
    </div>

</div>

<!-- LOGS -->
<div class="box" style="margin-top:10px;">
    <h3>📜 Logs</h3>
    <div id="logs" class="scroll-box" style="height:100px;"></div>
</div>

<script>
    let activeBots = []; // Stores Bot Objects
    let isRunning = false;

    // --- UTILS ---
    function log(msg) {
        let box = document.getElementById("logs");
        let div = document.createElement("div");
        div.innerText = "> " + msg;
        box.prepend(div);
    }

    function generateId(len=16) {
        let c = "abcdef0123456789", s = "";
        for(let i=0; i<len; i++) s += c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    function updateBotStatus(user, status) {
        let box = document.getElementById("botStatusList");
        let existing = document.getElementById("st-" + user);
        let colorClass = status === "ONLINE" ? "st-online" : (status === "FAILED" ? "st-fail" : "st-wait");
        let html = `<span class="${colorClass}">${user}</span> <span>[${status}]</span>`;

        if (existing) existing.innerHTML = html;
        else {
            let div = document.createElement("div");
            div.id = "st-" + user;
            div.className = "status-row";
            div.innerHTML = html;
            box.appendChild(div);
        }
    }

    function removeFailedID(badUser) {
        let area = document.getElementById("accountString");
        let regex = new RegExp(badUser + "#[^@]+@?", "g");
        area.value = area.value.replace(regex, "");
        log(`🗑️ Deleted Bad ID: ${badUser}`);
    }

    function updateRoomList(users) {
        let box = document.getElementById("roomUserList");
        box.innerHTML = "";
        document.getElementById("userCount").innerText = users.length;
        users.forEach(u => {
            let name = u.username || "Unknown";
            let icon = u.avatar_url || u.icon || "https://ui-avatars.com/api/?name="+name;
            if(!icon.startsWith("http")) icon = "https://chatp.net" + icon;
            
            let div = document.createElement("div");
            div.className = "user-item";
            div.innerHTML = `<img src="${icon}" class="user-avatar"><span>${name}</span>`;
            box.appendChild(div);
        });
    }

    // --- BOT LOGIC ---
    const ASCII_LIB = ["(｡♥‿♥｡)", "ʕ•ᴥ•ʔ", "✨🌟✨", "🔥", "❤️", "(ง'̀-'́)ง"];

    class Bot {
        constructor(user, pass, room) {
            this.user = user;
            this.pass = pass;
            this.room = room;
            this.ws = null;
            this.id = generateId();
            this.isJoined = false;
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

                if (data.handler === "login_event" && data.type === "success") {
                    this.send({ handler: "room_join", id: generateId(), name: this.room });
                }
                else if (data.handler === "login_event" && data.type === "error") {
                    updateBotStatus(this.user, "FAILED");
                    removeFailedID(this.user);
                    this.ws.close();
                }
                else if (data.handler === "room_event" && data.type === "room_joined") {
                    this.isJoined = true;
                    updateBotStatus(this.user, "ONLINE");
                    
                    // --- AUTO MESSAGE LOGIC ---
                    let mode = document.getElementById("msgMode").value;
                    let delay = document.getElementById("msgDelay").value * 1000;
                    let txt = document.getElementById("customText").value || "Hello";

                    if (mode !== "ghost") {
                        let finalMsg = (mode === "ascii") ? ASCII_LIB[Math.floor(Math.random()*ASCII_LIB.length)] : txt;
                        
                        log(`[${this.user}] Waiting ${delay/1000}s to send...`);
                        setTimeout(() => {
                            if(isRunning && this.ws.readyState === WebSocket.OPEN) {
                                this.sendMessage(finalMsg);
                            }
                        }, delay);
                    }
                }
                else if (data.handler === "roster") {
                    if (data.users) updateRoomList(data.users);
                }
            };

            this.ws.onclose = () => {
                this.isJoined = false;
                updateBotStatus(this.user, "DISCONNECTED");
            };
        }

        send(json) {
            if (this.ws.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(json));
        }

        sendMessage(text) {
            this.send({ 
                handler: "room_message", 
                id: generateId(), 
                room: this.room, 
                type: "text", 
                body: text 
            });
            log(`[${this.user}] Sent: ${text}`);
        }
    }

    // --- CONTROLS ---

    function startBots() {
        if (isRunning) return;
        let room = document.getElementById("roomName").value;
        let raw = document.getElementById("accountString").value;
        
        if (!raw.includes("#")) { alert("Enter accounts!"); return; }

        isRunning = true;
        activeBots = [];
        document.getElementById("botStatusList").innerHTML = "";

        let list = raw.split("@").filter(s => s.includes("#"));
        log(`[*] Launching ${list.length} bots...`);

        list.forEach((acc, i) => {
            let [u, p] = acc.split("#");
            setTimeout(() => {
                if(!isRunning) return;
                let bot = new Bot(u.trim(), p.trim(), room);
                activeBots.push(bot);
                bot.connect();
            }, i * 800);
        });
    }

    function stopBots() {
        isRunning = false;
        log("🛑 Stopping...");
        activeBots.forEach(b => { if(b.ws) b.ws.close(); });
        activeBots = [];
    }

    function forceSend() {
        let txt = document.getElementById("customText").value;
        let mode = document.getElementById("msgMode").value;
        
        if (!txt && mode === "custom") { alert("Enter a message first!"); return; }
        
        log(`🔊 FORCING MESSAGE to ${activeBots.length} bots...`);
        
        activeBots.forEach(bot => {
            if (bot.isJoined) {
                let msg = (mode === "ascii") ? ASCII_LIB[Math.floor(Math.random()*ASCII_LIB.length)] : txt;
                bot.sendMessage(msg);
            }
        });
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
