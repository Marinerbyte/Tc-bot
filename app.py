from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS LIVE MONITOR</title>
    <style>
        /* MATRIX THEME */
        body { background-color: #0d0d0d; color: #00ff41; font-family: 'Consolas', monospace; margin: 0; padding: 5px; height: 100vh; display: flex; flex-direction: column; }
        
        /* HEADER */
        header { border-bottom: 1px solid #00ff41; padding: 5px; display: flex; justify-content: space-between; align-items: center; }
        h3 { margin: 0; }

        /* MAIN LAYOUT */
        .main-grid { display: grid; grid-template-columns: 250px 1fr 200px; gap: 5px; flex: 1; overflow: hidden; margin-top: 5px; }
        @media (max-width: 800px) { .main-grid { grid-template-columns: 1fr; grid-template-rows: auto 1fr auto; } }

        /* PANELS */
        .panel { border: 1px solid #333; background: #111; padding: 5px; display: flex; flex-direction: column; overflow: hidden; }
        
        /* CONTROLS (LEFT) */
        .control-panel input, .control-panel textarea, .control-panel select { 
            width: 100%; background: #000; color: #fff; border: 1px solid #444; 
            padding: 5px; margin-bottom: 5px; box-sizing: border-box; font-size: 11px;
        }
        .control-panel textarea { height: 80px; color: yellow; }
        button { width: 100%; padding: 8px; font-weight: bold; cursor: pointer; border: none; margin-top: 5px; }
        .btn-green { background: #006400; color: white; }
        .btn-red { background: #8b0000; color: white; }
        .btn-orange { background: #ff8c00; color: black; }

        /* CHAT FEED (CENTER) */
        .chat-feed { flex: 1; overflow-y: scroll; background: #050505; padding: 10px; }
        .msg-row { margin-bottom: 5px; font-size: 12px; word-wrap: break-word; border-bottom: 1px solid #1a1a1a; padding-bottom: 2px; }
        .msg-time { color: #555; font-size: 10px; margin-right: 5px; }
        .msg-user { font-weight: bold; color: #00ced1; margin-right: 5px; }
        .msg-bot { color: #00ff41; font-weight: bold; } /* My Bots */
        .msg-text { color: #ddd; }

        /* USER LIST (RIGHT) */
        .user-list { overflow-y: scroll; font-size: 11px; }
        .user-item { display: flex; align-items: center; gap: 5px; padding: 3px; border-bottom: 1px solid #222; }
        .u-pic { width: 20px; height: 20px; border-radius: 50%; background: #333; }
        .u-name { color: #fff; }
        .u-count { text-align: center; background: #222; padding: 2px; margin-bottom: 5px; color: yellow; }

        /* BOT STATUS GRID */
        .bot-status-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 2px; max-height: 80px; overflow-y: auto; margin-top: 5px; }
        .b-badge { font-size: 9px; padding: 2px; background: #222; text-align: center; }
        .b-on { color: lime; border: 1px solid lime; }
        .b-off { color: red; border: 1px solid red; }
    </style>
</head>
<body>

<header>
    <h3>NEXUS MONITOR</h3>
    <div style="font-size:10px;">IP: CLIENT-SIDE (MOBILE)</div>
</header>

<div class="main-grid">
    
    <!-- 1. SETTINGS PANEL -->
    <div class="panel control-panel">
        <label>🎯 Target Room</label>
        <input type="text" id="roomName" value="ملتقى🥂العرب">

        <label>📝 Bots (user#pass@...)</label>
        <textarea id="accString" placeholder="bot1#pass123@bot2#pass123@"></textarea>

        <div style="display:flex; gap:2px;">
            <input type="number" id="spamSpeed" value="2000" placeholder="Speed (ms)" title="Loop Speed">
            <select id="msgMode">
                <option value="custom">Text</option>
                <option value="ascii">ASCII</option>
            </select>
        </div>

        <input type="text" id="customMsg" placeholder="Message...">

        <button class="btn-green" onclick="startSystem()">🚀 CONNECT</button>
        <button class="btn-orange" onclick="forceSend()">🔊 SEND NOW</button>
        <button class="btn-red" onclick="stopSystem()">🛑 STOP</button>

        <div style="border-top:1px solid #333; margin-top:5px; padding-top:2px; font-size:10px; color:#aaa;">BOT STATUS:</div>
        <div id="botGrid" class="bot-status-grid"></div>
    </div>

    <!-- 2. LIVE CHAT FEED -->
    <div class="panel">
        <div style="border-bottom:1px solid #333; margin-bottom:5px; color:#aaa; font-size:11px;">📡 LIVE ROOM FEED</div>
        <div id="chatFeed" class="chat-feed"></div>
    </div>

    <!-- 3. LIVE USER LIST -->
    <div class="panel">
        <div class="u-count">Users: <span id="uCount">0</span></div>
        <div id="userList" class="user-list"></div>
    </div>

</div>

<script>
    let activeBots = [];
    let isRunning = false;
    let spamInterval = null;
    
    // Map to store unique users in room
    let usersMap = new Map();
    let myBotNames = []; // To highlight my bots in chat

    // --- HELPER: ID GENERATOR ---
    function genId(len=16) {
        let c="abcdef0123456789", s="";
        for(let i=0; i<len; i++) s += c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    // --- UI UPDATES ---
    function addChatMessage(from, body, isMe) {
        let box = document.getElementById("chatFeed");
        let div = document.createElement("div");
        div.className = "msg-row";
        
        let time = new Date().toLocaleTimeString().split(" ")[0];
        let userClass = isMe ? "msg-bot" : "msg-user";
        
        div.innerHTML = `
            <span class="msg-time">[${time}]</span>
            <span class="${userClass}">${from}:</span>
            <span class="msg-text">${body}</span>
        `;
        box.appendChild(div);
        box.scrollTop = box.scrollHeight; // Auto Scroll
    }

    function renderUserList() {
        let box = document.getElementById("userList");
        box.innerHTML = "";
        document.getElementById("uCount").innerText = usersMap.size;

        usersMap.forEach((u) => {
            let name = u.name || u.username || "Unknown";
            // Check if this user is one of our bots
            let isMyBot = myBotNames.includes(name);
            let nameColor = isMyBot ? "lime" : "white";
            
            let icon = u.avatar_url || u.icon || "https://ui-avatars.com/api/?name="+name;
            if(!icon.startsWith("http")) icon = "https://chatp.net" + icon;

            let row = document.createElement("div");
            row.className = "user-item";
            row.innerHTML = `
                <img src="${icon}" class="u-pic">
                <span class="u-name" style="color:${nameColor}">${name}</span>
            `;
            box.appendChild(row);
        });
    }

    function updateBotStatus(user, status) {
        let grid = document.getElementById("botGrid");
        let id = "st-" + user;
        let el = document.getElementById(id);
        
        let cls = status === "ON" ? "b-on" : "b-off";
        
        if(!el) {
            el = document.createElement("div");
            el.id = id;
            grid.appendChild(el);
        }
        el.className = "b-badge " + cls;
        el.innerText = user;
    }

    // --- BOT LOGIC ---
    const ASCII = ["(｡♥‿♥｡)", "ʕ•ᴥ•ʔ", "🔥", "❤️", "⚡", "🚀", "💀"];

    class Bot {
        constructor(user, pass, room, isMaster) {
            this.user = user;
            this.pass = pass;
            this.room = room;
            this.ws = null;
            this.joined = false;
            this.isMaster = isMaster; // Only Master listens to chat/roster
        }

        connect() {
            if(!isRunning) return;
            updateBotStatus(this.user, "...");
            
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
                
                // 1.1 LOGIN FAIL
                else if(data.handler === "login_event" && data.type === "error") {
                    updateBotStatus(this.user, "OFF");
                    this.ws.close();
                }

                // 2. JOINED
                else if(data.handler === "room_event" && data.type === "room_joined") {
                    this.joined = true;
                    updateBotStatus(this.user, "ON");
                }

                // --- MASTER BOT ONLY TASKS (To avoid duplicate UI) ---
                if (this.isMaster) {
                    
                    // A. USER LIST (ROSTER)
                    if (data.handler === "roster" && data.users) {
                        data.users.forEach(u => usersMap.set(u.id || u.user_id, u));
                        renderUserList();
                    }
                    
                    // B. LIVE JOIN/LEAVE
                    if (data.handler === "room_event" && data.type === "join") {
                        usersMap.set(data.id || data.user_id, data);
                        renderUserList();
                    }
                    if (data.handler === "room_event" && data.type === "leave") {
                        usersMap.delete(data.id || data.user_id);
                        renderUserList();
                    }

                    // C. CHAT FEED
                    if ((data.handler === "room_message" || data.handler === "chat_message") && data.type === "text") {
                        let isMe = myBotNames.includes(data.from);
                        addChatMessage(data.from, data.body, isMe);
                    }
                }
            };

            this.ws.onclose = () => {
                this.joined = false;
                updateBotStatus(this.user, "OFF");
            };
        }

        send(json) {
            if(this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify(json));
            }
        }

        sendMessage(txt) {
            if(!this.joined) return;
            // CRITICAL FIX: length: "" (Empty String)
            this.send({
                handler: "room_message", id: genId(), room: this.room,
                type: "text", body: txt, url: "", length: "" 
            });
        }
    }

    // --- CONTROLLER ---
    function startSystem() {
        if(isRunning) return;
        
        let room = document.getElementById("roomName").value;
        let raw = document.getElementById("accString").value;
        if(!raw.includes("#")) { alert("Enter Bots!"); return; }

        isRunning = true;
        usersMap.clear();
        document.getElementById("userList").innerHTML = "";
        document.getElementById("chatFeed").innerHTML = "";
        document.getElementById("botGrid").innerHTML = "";
        
        let list = raw.split("@").filter(s => s.includes("#"));
        activeBots = [];
        myBotNames = [];

        list.forEach((acc, i) => {
            let [u, p] = acc.split("#");
            let cleanU = u.trim();
            myBotNames.push(cleanU);
            
            // Only the first bot is "Master" (handles UI updates)
            let isMaster = (i === 0);
            let bot = new Bot(cleanU, p.trim(), room, isMaster);
            
            activeBots.push(bot);
            
            // Stagger connections
            setTimeout(() => { if(isRunning) bot.connect(); }, i * 800);
        });

        // AUTO SPAM LOOP
        let speed = document.getElementById("spamSpeed").value;
        spamInterval = setInterval(() => {
            if(!isRunning) return;
            forceSend();
        }, speed);
    }

    function forceSend() {
        let mode = document.getElementById("msgMode").value;
        let txt = document.getElementById("customMsg").value || "Hello";
        
        activeBots.forEach(b => {
            if(b.joined) {
                let msg = (mode === "ascii") ? ASCII[Math.floor(Math.random()*ASCII.length)] : txt;
                b.sendMessage(msg);
            }
        });
    }

    function stopSystem() {
        isRunning = false;
        clearInterval(spamInterval);
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
