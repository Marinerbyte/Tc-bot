from flask import Flask, render_template_string

app = Flask(__name__)

# --- HTML + JS DASHBOARD ---
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Remanu Bot Panel</title>
    <style>
        body { background-color: #000; color: #00ff00; font-family: monospace; padding: 15px; }
        .container { max-width: 100%; margin: auto; }
        h2 { text-align: center; border-bottom: 1px solid green; padding-bottom: 10px; }
        
        label { font-weight: bold; display: block; margin-top: 10px; color: #fff; }
        
        input, textarea { 
            width: 100%; background: #222; color: #fff; border: 1px solid #555; 
            padding: 10px; margin-top: 5px; box-sizing: border-box; border-radius: 5px;
        }
        
        /* Input Box for ID String */
        textarea { height: 120px; font-size: 13px; font-family: monospace; color: yellow; }

        button { 
            width: 100%; padding: 15px; font-weight: bold; cursor: pointer; 
            border: none; margin-top: 15px; font-size: 16px; border-radius: 5px;
        }
        .btn-start { background: green; color: white; }
        .btn-stop { background: red; color: white; }
        
        #logs { 
            height: 300px; overflow-y: scroll; border: 1px solid #333; 
            padding: 5px; font-size: 11px; margin-top: 20px; background: #050505;
        }
        .log-entry { border-bottom: 1px solid #222; padding: 2px; }
    </style>
</head>
<body>

<div class="container">
    <h2>🤖 Remanu Bot Controller</h2>
    <p style="text-align:center; color: #777; font-size: 12px;">Runs on YOUR Mobile Data (IP)</p>

    <label>🎯 Target Room:</label>
    <input type="text" id="roomName" value="ملتقى🥂العرب">
    
    <label>📝 Paste IDs (Format: user#pass@user#pass@)</label>
    <textarea id="accountString" placeholder="raj#123@mohit#456@ali#789@"></textarea>

    <button class="btn-start" onclick="startBots()">🚀 LAUNCH BOTS</button>
    <button class="btn-stop" onclick="stopBots()">🛑 STOP ALL</button>

    <h3>📜 Logs</h3>
    <div id="logs"></div>
</div>

<script>
    let activeSockets = [];
    let isRunning = false;

    function log(msg) {
        let box = document.getElementById("logs");
        let div = document.createElement("div");
        div.className = "log-entry";
        div.innerText = "> " + msg;
        box.prepend(div);
    }

    function generateId(len=16) {
        let c = "abcdef0123456789";
        let s = "";
        for(let i=0; i<len; i++) s += c.charAt(Math.floor(Math.random()*c.length));
        return s;
    }

    class Bot {
        constructor(user, pass, room) {
            this.user = user;
            this.pass = pass;
            this.room = room;
            this.ws = null;
            this.id = generateId();
        }

        connect() {
            if (!isRunning) return;
            
            // Mobile Browser to Chatp Direct Connection
            this.ws = new WebSocket("wss://chatp.net:5333/server");

            this.ws.onopen = () => {
                log(`[${this.user}] Connected. Logging in...`);
                this.send({
                    handler: "login",
                    id: this.id,
                    username: this.user,
                    password: this.pass
                });
            };

            this.ws.onmessage = (e) => {
                if (!isRunning) return;
                let data = JSON.parse(e.data);

                if (data.handler === "login_event" && data.type === "success") {
                    log(`[${this.user}] Login OK! Joining Room...`);
                    this.send({
                        handler: "room_join",
                        id: generateId(),
                        name: this.room
                    });
                }
                else if (data.handler === "room_event" && data.type === "room_joined") {
                    log(`[${this.user}] ✅ ENTERED ROOM`);
                }
            };

            this.ws.onclose = () => log(`[${this.user}] Disconnected ❌`);
            this.ws.onerror = () => log(`[${this.user}] Connection Error ⚠️`);
            
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

        if (!rawString.includes("#") || !rawString.includes("@")) {
            alert("Format Error! Use: user#pass@user#pass@");
            return;
        }

        isRunning = true;
        log("[*] Parsing Accounts...");

        // --- PARSING LOGIC (Format: id#pass@id#pass@) ---
        // 1. Split by '@' to get accounts
        let accounts = rawString.split("@");
        let validBots = [];

        accounts.forEach(acc => {
            acc = acc.trim();
            if (acc.includes("#")) {
                let parts = acc.split("#");
                let u = parts[0].trim();
                let p = parts[1].trim();
                if (u && p) {
                    validBots.push({u: u, p: p});
                }
            }
        });

        log(`[*] Found ${validBots.length} Bots. Launching...`);

        // Connect one by one with 500ms delay
        validBots.forEach((botData, index) => {
            setTimeout(() => {
                if (!isRunning) return;
                let bot = new Bot(botData.u, botData.p, room);
                bot.connect();
            }, index * 500);
        });
    }

    function stopBots() {
        isRunning = false;
        log("[!] Stopping all bots...");
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
