from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NEXUS BLACKOUT</title>
    <style>
        /* --- THEME: DARK MATTER --- */
        :root {
            --bg: #000000;
            --panel: #0a0a0a;
            --border: #333;
            --accent: #00ff00; /* Toxic Green */
            --danger: #ff0000; /* Red */
            --spy: #00ccff;    /* Cyan */
            --text: #ffffff;
        }

        body { 
            background-color: var(--bg); color: var(--text); 
            font-family: 'Courier New', monospace; margin: 0; padding: 0;
            height: 100vh; display: flex; flex-direction: column; overflow: hidden;
        }

        /* --- TABS --- */
        .tabs { display: flex; height: 50px; background: #050505; border-bottom: 2px solid var(--accent); }
        .tab-btn {
            flex: 1; display: flex; align-items: center; justify-content: center;
            font-weight: bold; font-size: 12px; cursor: pointer; color: #555;
            border-right: 1px solid #111; transition: 0.2s;
        }
        .tab-btn.active { background: #111; color: var(--accent); border-bottom: 3px solid var(--accent); }
        .t-attack.active { color: var(--danger); border-color: var(--danger); }
        .t-spy.active { color: var(--spy); border-color: var(--spy); }

        /* --- PAGES --- */
        .page { display: none; padding: 10px; height: calc(100vh - 50px); overflow-y: auto; }
        .page.active { display: block; }

        /* --- COMPONENTS --- */
        .box { background: var(--panel); border: 1px solid var(--border); padding: 10px; margin-bottom: 10px; border-radius: 4px; }
        .box-title { 
            font-size: 11px; font-weight: bold; border-bottom: 1px dashed #333; 
            padding-bottom: 5px; margin-bottom: 10px; color: #888; display: flex; justify-content: space-between;
        }

        input, textarea, select {
            width: 100%; background: #000; border: 1px solid #444; color: #fff;
            padding: 8px; margin-top: 4px; font-family: monospace; font-size: 11px; box-sizing: border-box;
        }
        textarea { height: 70px; color: yellow; resize: vertical; }
        
        .btn-row { display: flex; gap: 5px; margin-top: 10px; }
        button {
            flex: 1; padding: 12px; font-weight: bold; cursor: pointer; border: none; 
            border-radius: 2px; font-size: 11px; color: white; text-transform: uppercase;
        }
        .b-green { background: #006400; border: 1px solid var(--accent); }
        .b-red { background: #640000; border: 1px solid var(--danger); }
        .b-cyan { background: #004466; border: 1px solid var(--spy); }

        /* --- LISTS --- */
        .scroll { height: 180px; overflow-y: auto; background: #020202; border: 1px solid #222; padding: 5px; font-size: 11px; }
        
        /* CHAT BUBBLES */
        .msg { margin-bottom: 4px; border-bottom: 1px solid #111; padding: 2px; word-wrap: break-word; }
        .time { color: #444; font-size: 9px; margin-right: 5px; }
        .usr { font-weight: bold; color: #aaa; }
        .txt { color: #ddd; }
        
        /* Highlight Effects */
        .my-msg .usr { color: var(--accent); } /* Sent by us */
        .tgt-msg .usr { color: var(--danger); } /* Target */
        .tgt-msg { background: rgba(255, 0, 0, 0.1); border-left: 2px solid var(--danger); }

        /* USER ROWS */
        .u-row { display: flex; align-items: center; justify-content: space-between; padding: 6px; border-bottom: 1px solid #151515; cursor: pointer; }
        .u-row:hover { background: #111; }
        .u-pic { width: 24px; height: 24px; border-radius: 50%; border: 1px solid #333; margin-right: 8px; }
        
        .badge { font-size: 8px; padding: 2px 4px; border-radius: 2px; border: 1px solid #333; }
        .bdg-bot { color: var(--accent); border-color: var(--accent); }
        .bdg-tgt { color: var(--danger); border-color: var(--danger); animation: pulse 1s infinite; }

        @keyframes pulse { 50% { opacity: 0.5; } }
    </style>
</head>
<body>

<!-- NAVIGATION -->
<div class="tabs">
    <div class="tab-btn active" onclick="go('dash', this)">1. DASHBOARD</div>
    <div class="tab-btn t-attack" onclick="go('attack', this)">2. ATTACK</div>
    <div class="tab-btn t-spy" onclick="go('spy', this)">3. SPY</div>
</div>

<!-- PAGE 1: DASHBOARD -->
<div id="dash" class="page active">
    <div class="box">
        <div class="box-title"><span>📡 CONNECTION</span></div>
        <label>TARGET ROOM</label>
        <input type="text" id="room" value="ملتقى🥂العرب">
        
        <label>BOT ACCOUNTS</label>
        <textarea id="accs" placeholder="bot1#pass123@bot2#pass123@"></textarea>
        
        <div class="btn-row">
            <button class="b-green" onclick="connectAll()">🔌 INITIALIZE</button>
            <button class="b-red" onclick="killAll()">❌ TERMINATE</button>
        </div>
    </div>

    <div class="box">
        <div class="box-title">
            <span>🤖 ACTIVE BOTS (<span id="cntBot">0</span>)</span>
        </div>
        <div id="botList" class="scroll" style="height:120px;"></div>
    </div>
    
    <div class="box">
        <div class="box-title">📜 SYSTEM LOGS</div>
        <div id="sysLogs" class="scroll" style="height:100px; color:#777;"></div>
    </div>
</div>

<!-- PAGE 2: ATTACK -->
<div id="attack" class="page">
    <div class="box" style="border-color: var(--danger);">
        <div class="box-title" style="color:var(--danger)">⚔️ ATTACK CONFIG</div>
        
        <div style="display:flex; gap:5px;">
            <div style="flex:1"><label>SPEED (ms)</label><input type="number" id="speed" value="2000"></div>
            <div style="flex:1"><label>BURST</label><input type="number" id="burst" value="1"></div>
        </div>

        <div style="display:flex; gap:5px; margin-top:5px;">
            <select id="mode" style="flex:1">
                <option value="custom">Custom Text</option>
                <option value="ascii">Random ASCII</option>
            </select>
        </div>
        
        <input type="text" id="spamText" placeholder="Message content...">

        <div class="btn-row">
            <button class="b-red" id="btnSpam" onclick="toggleSpam()">🔥 START FIRE</button>
            <button class="b-green" onclick="forceFire()">🔊 1 SHOT</button>
        </div>
    </div>

    <div class="box">
        <div class="box-title"><span>📡 BATTLEFIELD VIEW</span></div>
        <div id="attackFeed" class="scroll" style="height:250px;"></div>
    </div>
</div>

<!-- PAGE 3: SPY -->
<div id="spy" class="page">
    <div class="box" style="border-color: var(--spy);">
        <div class="box-title" style="color:var(--spy)">
            <span>👁️ TARGET LIST</span>
            <span id="tgtCount" style="color:white">0 Locked</span>
        </div>
        <div style="text-align:center; font-size:10px; color:#555; margin-bottom:5px;">TAP USERS TO TARGET</div>
        
        <div class="btn-row">
            <button class="b-cyan" id="btnCopy" onclick="toggleCopy()">🦜 COPYCAT: OFF</button>
            <button class="b-green" onclick="dlChat()">💾 EXPORT</button>
        </div>
        <button class="b-red" style="width:100%; margin-top:5px;" onclick="clearTgt()">UNLOCK ALL</button>
    </div>

    <!-- SPLIT VIEW -->
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:5px;">
        <div class="box" style="margin:0;">
            <div class="box-title">👥 USERS (<span id="cntUser">0</span>)</div>
            <div id="userList" class="scroll" style="height:250px;"></div>
        </div>
        <div class="box" style="margin:0;">
            <div class="box-title">🎯 TARGET LOGS</div>
            <div id="spyFeed" class="scroll" style="height:250px;"></div>
        </div>
    </div>
</div>

<script>
    // --- VARIABLES ---
    let bots = [];
    let isConnected = false;
    let isSpamming = false;
    let isCopy = false;
    let spamTimer = null;
    
    let users = new Map(); // Room Users
    let targets = new Set(); // Targets
    let myNames = []; // Bot Usernames
    
    let logs = []; // For Export

    // --- NAVIGATION ---
    function go(page, btn) {
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(page).classList.add('active');
        btn.classList.add('active');
    }

    function log(msg) {
        let d = document.createElement("div");
        d.innerText = "> " + msg;
        document.getElementById("sysLogs").prepend(d);
    }

    // --- GEN ID (20 CHARS - FROM TANVAR.PY) ---
    function genId(len=20) {
        let c="abcdef0123456789",s="";
        for(let i=0;i<len;i++) s+=c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    // --- UI RENDERERS ---
    function renderBots() {
        let box = document.getElementById("botList");
        box.innerHTML = "";
        document.getElementById("cntBot").innerText = bots.length;
        
        bots.forEach(b => {
            let color = b.joined ? "lime" : "red";
            let st = b.joined ? "ONLINE" : "WAIT";
            box.innerHTML += `<div style="display:flex; justify-content:space-between; border-bottom:1px solid #222; padding:3px;">
                <span>${b.user}</span> <span style="color:${color}">${st}</span>
            </div>`;
        });
    }

    function renderUsers() {
        let box = document.getElementById("userList");
        box.innerHTML = "";
        document.getElementById("cntUser").innerText = users.size;

        users.forEach(u => {
            let name = u.name || u.username || "Unknown";
            let icon = u.avatar_url || u.icon || "https://ui-avatars.com/api/?name="+name;
            if(!icon.startsWith("http")) icon = "https://chatp.net"+icon;

            let isMe = myNames.includes(name);
            let isTgt = targets.has(name);
            
            let badge = "";
            if(isMe) badge = `<span class="badge bdg-bot">BOT</span>`;
            if(isTgt) badge = `<span class="badge bdg-tgt">TARGET</span>`;

            let d = document.createElement("div");
            d.className = "u-row";
            d.onclick = () => toggleTgt(name);
            d.innerHTML = `
                <div style="display:flex; align-items:center;">
                    <img src="${icon}" class="u-pic">
                    <span style="color:${isTgt?'var(--danger)':'#ddd'}">${name}</span>
                </div>
                ${badge}
            `;
            box.appendChild(d);
        });
    }

    function addChat(from, msg) {
        let time = new Date().toLocaleTimeString().split(" ")[0];
        let isMe = myNames.includes(from);
        let isTgt = targets.has(from);
        
        let cls = isMe ? "my-msg" : (isTgt ? "tgt-msg" : "");
        
        let html = `
            <div class="msg ${cls}">
                <span class="time">${time}</span>
                <span class="usr">${from}:</span>
                <span class="txt">${msg}</span>
            </div>
        `;

        // Add to Attack Feed
        let af = document.getElementById("attackFeed");
        af.insertAdjacentHTML('beforeend', html);
        af.scrollTop = af.scrollHeight;

        // If Target, Add to Spy Feed
        if(isTgt) {
            let sf = document.getElementById("spyFeed");
            sf.insertAdjacentHTML('beforeend', html);
            sf.scrollTop = sf.scrollHeight;
            logs.push(`[${time}] ${from}: ${msg}`);
            
            // COPYCAT TRIGGER
            if(isCopy && isConnected) broadcast(msg);
        }
    }

    // --- SPY LOGIC ---
    function toggleTgt(name) {
        if(targets.has(name)) targets.delete(name);
        else targets.add(name);
        document.getElementById("tgtCount").innerText = targets.size + " Locked";
        renderUsers();
    }
    function clearTgt() { targets.clear(); renderUsers(); }
    
    function toggleCopy() {
        isCopy = !isCopy;
        let btn = document.getElementById("btnCopy");
        btn.innerText = isCopy ? "🦜 COPY: ON" : "🦜 COPY: OFF";
        btn.style.borderColor = isCopy ? "var(--danger)" : "var(--spy)";
    }

    function dlChat() {
        if(logs.length===0) { alert("No logs!"); return; }
        let blob = new Blob([logs.join("\\n")], {type: "text/plain;charset=utf-8"});
        let a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "spy_logs.txt";
        a.click();
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
            this.isMaster = isMaster;
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
                    renderBots();
                }

                // MASTER EVENTS
                if(this.isMaster) {
                    if((data.handler === "roster" || data.handler === "room_users") && data.users) {
                        data.users.forEach(u => users.set(u.username, u));
                        renderUsers();
                    }
                    if(data.handler === "room_event" && data.type === "you_joined" && data.users) {
                        data.users.forEach(u => users.set(u.username, u));
                        renderUsers();
                    }
                    if(data.handler === "room_event" && data.type === "join") {
                        users.set(data.username, data); renderUsers();
                    }
                    if(data.handler === "room_event" && data.type === "leave") {
                        users.delete(data.username); renderUsers();
                    }
                    if(data.handler === "room_event" && data.type === "text") {
                        addChat(data.from, data.body);
                    }
                }
            };

            this.ws.onclose = () => { this.joined = false; renderBots(); };
        }

        send(json) {
            if(this.ws && this.ws.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(json));
        }

        sendMessage(txt) {
            if(!this.joined) return;
            // *** CRITICAL FIX FROM TANVAR.PY ***
            // id: 20 chars
            // url: ""
            // length: "" (Empty String)
            this.send({
                handler: "room_message", id: genId(), room: this.room,
                type: "text", body: txt, url: "", length: ""
            });
        }
        
        disconnect() { if(this.ws) this.ws.close(); }
    }

    // --- CONTROLLER ---
    function connectAll() {
        if(isConnected) return;
        let room = document.getElementById("room").value;
        let raw = document.getElementById("accs").value;
        if(!raw.includes("#")) { alert("Enter Bots!"); return; }

        users.clear(); myNames=[]; bots=[];
        renderUsers(); renderBots();

        let list = raw.split("@").filter(s => s.includes("#"));
        list.forEach((s, i) => {
            let [u, p] = s.split("#");
            myNames.push(u.trim());
            let bot = new Bot(u.trim(), p.trim(), room, (i===0));
            bots.push(bot);
            setTimeout(() => bot.connect(), i*600);
        });
        isConnected = true;
        log("System Online.");
    }

    function broadcast(msg) {
        let burst = parseInt(document.getElementById("burst").value) || 1;
        bots.forEach(b => {
            if(b.joined) {
                for(let k=0; k<burst; k++) b.sendMessage(msg);
            }
        });
    }

    function forceFire() {
        let txt = document.getElementById("spamText").value || "Test";
        broadcast(txt);
    }

    function toggleSpam() {
        let btn = document.getElementById("btnSpam");
        if(isSpamming) {
            isSpamming = false;
            clearInterval(spamInterval);
            btn.innerText = "🔥 START FIRE";
            btn.classList.replace("b-green", "b-red");
        } else {
            isSpamming = true;
            btn.innerText = "⏸️ STOP";
            btn.classList.replace("b-red", "b-green");
            let speed = parseInt(document.getElementById("speed").value);
            
            spamInterval = setInterval(() => {
                let mode = document.getElementById("mode").value;
                let txt = document.getElementById("spamText").value || ".";
                if(mode==="ascii") txt = ASCII[Math.floor(Math.random()*ASCII.length)];
                broadcast(txt);
            }, speed);
        }
    }

    function killAll() {
        if(isSpamming) toggleSpam();
        bots.forEach(b => b.disconnect());
        bots = [];
        isConnected = false;
        renderBots();
        log("Terminated.");
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