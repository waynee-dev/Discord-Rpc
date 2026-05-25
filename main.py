import websocket
import json
import time
import threading

TOKEN = "ACCOUNT TOKEN"
APP_ID = "APPLICATION ID"
APP_NAME = "APPLICATION NAME"

LARGE_IMAGE = ""
LARGE_TEXT  = ""
SMALL_IMAGE = ""
SMALL_TEXT  = ""

WS_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
seq = None
START_TIME = int(time.time() * 1000)

def make_activity():
    act = {
        "name": APP_NAME,
        "application_id": APP_ID,
        "type": 3, # 0 playing, 2 listening, 3 watching, 5 competing
        "timestamps": {"start": START_TIME}
    }

    assets = {}
    if LARGE_IMAGE: assets["large_image"] = LARGE_IMAGE
    if LARGE_TEXT:  assets["large_text"]  = LARGE_TEXT
    if SMALL_IMAGE: assets["small_image"] = SMALL_IMAGE
    if SMALL_TEXT:  assets["small_text"]  = SMALL_TEXT

    if assets:
        act["assets"] = assets

    return act

def handle_message(ws, raw):
    global seq

    msg = json.loads(raw)
    op  = msg.get("op")
    t   = msg.get("t")

    if msg.get("s"):
        seq = msg["s"]

    if op == 10:
        hb_ms = msg["d"]["heartbeat_interval"]

        def keep_alive():
            while True:
                time.sleep(hb_ms / 1000)
                ws.send(json.dumps({"op": 1, "d": seq}))
                print("heartbeat")

        threading.Thread(target=keep_alive, daemon=True).start()

        ws.send(json.dumps({
            "op": 2,
            "d": {
                "token": TOKEN,
                "properties": {
                    "os": "windows",
                    "browser": "Discord Client",
                    "device": ""
                },
                "presence": {
                    "since": 0,
                    "status": "online",
                    "afk": False,
                    "activities": [make_activity()]
                }
            }
        }))

    elif t == "READY":
        uname = msg["d"]["user"]["username"]
        print(f"Logged in as {uname}")

    elif op == 9:
        print("Session invalid, check your token")
        ws.close()

    elif op == 7:
        print("Server asked us to reconnect")
        ws.close()


def handle_error(ws, err):
    print(f"ws error: {err}")


def handle_close(ws, code, reason):
    print(f"Closed ({code})")


def handle_open(ws):
    print("Connected")

if __name__ == "__main__":
    print("Connecting...")
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=handle_open,
        on_message=handle_message,
        on_error=handle_error,
        on_close=handle_close
    )
    ws.run_forever()
