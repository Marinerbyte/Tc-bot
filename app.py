from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS DEBUGGER</title>
    <style>
        body { background: #000; color: #0f0; font-family: monospace; padding: 10px; }
        .box { border: 1px solid #444; padding: 10px; margin-bottom: 10px; background: #111; }
        
        input, textarea { width: 100%; background: #222; color: #fff; border: 1px solid #555; padding: 5px; box-sizing: border-box; }
        textarea { height: 60px; }
        
        button { width: 100%; padding: 10px; margin-top: 5px; cursor: pointer; font-weight: bold; border: none; }
        .btn-con { background: blue; color: white; }
        .btn-a { background: green; color: white; }
        .btn-b { background: orange; color: black; }
        .btn-c { background: purple; color: white; }
        .btn-kill { background: red; color: white; }

        #debug-log { 
            height: 300px; overflow-y: scroll; border: 1px solid #666; 
            padding: 5px; font-size: 10px; background: #000; white-space: pre-wrap;
        }
        .tx { color: cyan; } /* Sent */
        .rx { color: yellow; } /* Received */
        .err { color: red; }
    </style>
</head>
<body>

<h2 style="text-align:center; margin:0;">🛠️ DEBUG MODE</h2>
<p style="text-align:center; font-size:10px; color:#aaa;">Check the logs below to see why messages fail.</p>

<div class="box">
    <label>Room:</label>
    <input type="text" id="roomName" value="ملتقى🥂العرب">
    
    <label>Bot (user#pass):</label>
    <input type="text" id="botCreds" placeholder="id#pass">
    
    <button class="btn-con" onclick="connectBot()">1. CONNECT SINGLE BOT</button>
    <button class="btn-kill" onclick="killBot()">❌ DISCONNECT</button>
</div>

<div class="box">
    <label>Message Test:</label>
    <input type="text" id="msgText" value="Test Message">
    
    <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:5px;">
        <button class="btn-a" onclick="sendTypeA()">Method A</button>
        <button class="btn-b" onclick="sendTypeB()">Method B</button>
        <button class="btn-c" onclick="sendTypeC()">Method C</button>
    </div>
    <small style="color:#aaa;">Try all 3 buttons one by one.</small>
</div>

<h3>📡 SERVER LOGS (RAW):</h3>
<div id="debug-log"></div>

<script>
    let ws = null;
    let isConnected = false;
    let pingInterval = null;

    function log(text, type="rx") {
        let box = document.getElementById("debug-log");
        let d = document.createElement("div");
        d.className = type;
        d.innerText = (type === "tx" ? "📤 " : "📥 ") + text;
        box.prepend(d);
    }

    function genId(len=20) {
        let c="abcdef0123456789", s="";
        for(let i=0; i<len; i++) s += c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    function connectBot() {
        if(ws) { alert("Already connected!"); return; }
        
        let creds = document.getElementById("botCreds").value;
        if(!creds.includes("#")) { alert("Enter user#pass"); return; }
        let [u, p] = creds.split("#");
        let room = document.getElementById("roomName").value;

        ws = new WebSocket("wss://chatp.net:5333/server");

        ws.onopen = () => {
            log("Connected to Socket. Sending Login...", "tx");
            let loginData = { handler: "login", id: genId(), username: u, password: p };
            ws.send(JSON.stringify(loginData));
            
            // Keep Alive Ping (Every 30s)
            pingInterval = setInterval(() => {
                if(ws.readyState === WebSocket.OPEN) ws.send(""); // Empty packet for ping
            }, 30000);
        };

        ws.onmessage = (e) => {
            log(e.data, "rx"); // PRINT RAW SERVER RESPONSE
            
            let data = JSON.parse(e.data);
            
            // Auto Join on Login Success
            if(data.handler === "login_event" && data.type === "success") {
                log("Login Success! Joining Room...", "tx");
                ws.send(JSON.stringify({ handler: "room_join", id: genId(), name: room }));
            }
        };

        ws.onclose = () => {
            log("Socket Closed / Disconnected", "err");
            ws = null;
            clearInterval(pingInterval);
        };
        
        ws.onerror = (e) => log("Socket Error!", "err");
    }

    // --- TEST METHOD A: Standard (tanvar.py style) ---
    function sendTypeA() {
        if(!ws) return;
        let txt = document.getElementById("msgText").value;
        let room = document.getElementById("roomName").value;
        
        let payload = {
            handler: "room_message",
            id: genId(),
            room: room,
            type: "text",
            body: txt,
            url: "",
            length: ""
        };
        ws.send(JSON.stringify(payload));
        log("Sent Method A (Standard)", "tx");
    }

    // --- TEST METHOD B: With integer length ---
    function sendTypeB() {
        if(!ws) return;
        let txt = document.getElementById("msgText").value;
        let room = document.getElementById("roomName").value;
        
        let payload = {
            handler: "room_message",
            id: genId(),
            room: room,
            type: "text",
            body: txt,
            url: "",
            length: 0 // Try integer 0
        };
        ws.send(JSON.stringify(payload));
        log("Sent Method B (Length: 0)", "tx");
    }

    // --- TEST METHOD C: Minimal ---
    function sendTypeC() {
        if(!ws) return;
        let txt = document.getElementById("msgText").value;
        let room = document.getElementById("roomName").value;
        
        let payload = {
            handler: "room_message",
            id: genId(),
            room: room,
            type: "text",
            body: txt
        };
        ws.send(JSON.stringify(payload));
        log("Sent Method C (Minimal)", "tx");
    }

    function killBot() {
        if(ws) ws.close();
        ws = null;
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
