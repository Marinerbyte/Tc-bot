from flask import Flask, render_template_string

app = Flask(__name__)

# --- HTML + JS DASHBOARD ---
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Remanu 10-Bot Army</title>
    <style>
        body { background-color: #000; color: #00ff00; font-family: monospace; padding: 10px; }
        .container { max-width: 100%; margin: auto; }
        h1 { text-align: center; border-bottom: 1px solid green; padding-bottom: 10px; }
        
        .status-box { border: 1px solid #333; padding: 10px; margin-bottom: 15px; background: #111; }
        
        input { 
            width: 100%; background: #222; color: #fff; border: 1px solid #555; 
            padding: 10px; margin-bottom: 10px; box-sizing: border-box;
        }
        
        button { 
            width: 100%; padding: 15px; font-weight: bold; cursor: pointer; 
            border: none; margin-top: 5px; font-size: 16px;
        }
        .btn-start { background: green; color: white; }
        .btn-stop { background: red; color: white; }
        
        #logs { 
            height: 350px; overflow-y: scroll; border: 1px solid #333; 
            padding: 5px; font-size: 11px; margin-top: 20px; background: #050505;
        }
        .log-entry { border-bottom: 1px solid #222; padding: 2px; }
    </style>
</head>
<body>

<div class="container">
    <h1>🤖 10-Bot Controller</h1>
    <p style="text-align:center; color: #777;">Runs on YOUR Mobile IP</p>

    <div class="status-box">
        <label>🎯 Room Name:</label>
        <input type="text" id="roomName" value="ملتقى🥂العرب">
        
        <label>💬 Message (Optional):</label>
        <input type="text" id="msg" placeholder="Hello from Bot Army!">
    </div>

    <button class="btn-start" onclick="startArmy()">🚀 LAUNCH 10 BOTS</button>
    <button class="btn-stop" onclick="stopArmy()">🛑 STOP ALL</button>

    <h3>📜 Logs</h3>
    <div id="logs"></div>
</div>

<script>
    // ==========================================
    // 👇 YAHAN APNI 10 IDs DALEIN 👇
    // ==========================================
    const MY_BOTS = [
        { u: "id_number_1", p: "password123" },
        { u: "id_number_2", p: "password123" },
        { u: "id_number_3", p: "password123" },
        { u: "id_number_4", p: "password123" },
        { u: "id_number_5", p: "password123" },
        { u: "id_number_6", p: "password123" },
        { u: "id_number_7", p: "password123" },
        { u: "id_number_8", p: "password123" },
        { u: "id_number_9", p: "password123" },
        { u: "id_number_10", p: "password123" }
    ];
    // ==========================================

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
            
            // Connect directly from Mobile Browser
            this.ws = new WebSocket("wss://chatp.net:5333/server");

            this.ws.onopen = () => {
                log(`[${this.user}] Connected... Logging in`);
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

                // Login Success -> Join Room
                if (data.handler === "login_event" && data.type === "success") {
                    log(`[${this.user}] Login Success! Joining Room...`);
                    this.send({
                        handler: "room_join",
                        id: generateId(),
                        name: this.room
                    });
                }
                
                // Joined Room
                else if (data.handler === "room_event" && data.type === "room_joined") {
                    log(`[${this.user}] ENTERED ROOM! ✅`);
                    
                    // Optional: Send Message after 2 seconds
                    let msg = document.getElementById("msg").value;
                    if (msg) {
                        setTimeout(() => {
                            if(isRunning) {
                                this.send({
                                    handler: "room_message",
                                    id: generateId(),
                                    room: this.room,
                                    type: "text",
                                    body: msg
                                });
                                log(`[${this.user}] Message Sent!`);
                            }
                        }, 2000);
                    }
                }
            };

            this.ws.onclose = () => log(`[${this.user}] Disconnected ❌`);
            activeSockets.push(this.ws);
        }

        send(json) {
            if (this.ws.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(json));
        }
    }

    function startArmy() {
        if (isRunning) return;
        isRunning = true;
        let room = document.getElementById("roomName").value;
        
        log(`[*] Launching ${MY_BOTS.length} Bots on Mobile IP...`);

        // Har bot ko 0.5 second ke gap par connect karo taki browser hang na ho
        MY_BOTS.forEach((botData, index) => {
            setTimeout(() => {
                if (!isRunning) return;
                let bot = new Bot(botData.u, botData.p, room);
                bot.connect();
            }, index * 500);
        });
    }

    function stopArmy() {
        isRunning = false;
        log("[!] Stopping all connections...");
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
