import websocket
import threading
import random
import redis
import time
import json
import rel
import string
import random
import struct

import scraper.gateway

sessions = {}

CONTEXT = 10

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

import sys
sys.stdout = Unbuffered(sys.stdout)

r = redis.Redis(host='redis', decode_responses=True)

def heartbeat(ws, interval):
    time.sleep(interval * random.random())
    while True:
        ws.send(json.dumps({"op": 1, "d": None}))
        print("Sent heartbeat")
        time.sleep(interval)

def write_message(message):
    # write message to a table that is searchable by channel id
    r.lpush(f"messages:{message.channel_id}", json.dumps(message.data))

def get_context(message, num_messages=10) -> list[scraper.gateway.DiscordGatewayMessageCreate]:
    chan_id = message.channel_id
    messages = []
    for msg in r.lrange(f"messages:{chan_id}", 0, num_messages):
        if msg is None:
            break
        msg = json.loads(msg)
        msg = scraper.gateway.DiscordGatewayMessageCreate(msg)
        messages.append(msg)
    
    messages.reverse()

    return messages

def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def on_message(ws, message):
    msg = json.loads(message)
    parsed = scraper.gateway.GatewayParser.parse(msg)

    if isinstance(parsed, scraper.gateway.GatewayHelloEvent):
        heartbeat_interval = parsed.heartbeat_interval / 1000
        print("Heartbeat interval: " + str(heartbeat_interval) + " seconds")
        threading.Thread(
            target=heartbeat,
            args=(ws, heartbeat_interval),
            daemon=True
        ).start()

    if isinstance(parsed, scraper.gateway.DiscordGatewayMessageCreate):
        myself = "1129767250342195222"
        write_message(parsed)
        if parsed.channel_id in sessions:
            if sessions[parsed.channel_id][1] > CONTEXT or time.time() - sessions[parsed.channel_id][2] > 120:
                r.lpush(f"training_data", sessions[parsed.channel_id][0])
                del sessions[parsed.channel_id]

        if parsed.author.id == myself:
            context = get_context(parsed, num_messages=CONTEXT)
            format = ""
            did_i_just_talk = False

            for message in context:
                display_name = message.author.username
                if message.author.global_name is not None:
                    display_name = message.author.global_name

                if message.author.id == myself:
                    if did_i_just_talk:
                        format += f"\n{message.content}"
                    else:
                        format = format[:-16]
                        format += f"RESPONSE: {message.content}"
                    did_i_just_talk = True 
                else:
                    if did_i_just_talk:
                        format += f"<END>\n"
                    format += f"MESSAGE IN: (ID: {random_string()}, From: {display_name}) - {message.content}\n"
                    format += "RESPONSE: <END>\n"
                    did_i_just_talk = False
            
            if did_i_just_talk:
                format += f"<END>\n"

            if parsed.channel_id not in sessions:
                sessions[parsed.channel_id] = [format, 1, time.time()]
            else:
                sessions[parsed.channel_id][0] = format
                sessions[parsed.channel_id][1] += 1

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection and sent HELLO")
    helo = json.load(open("/app/data/helo.json"))
    ws.send(json.dumps(helo))

def ws_on_error(ws, error):
    raise error

if __name__ == "__main__":
    ws = websocket.WebSocketApp("wss://gateway.discord.gg/?encoding=json",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=ws_on_error,
                              on_close=on_close)
    

    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()