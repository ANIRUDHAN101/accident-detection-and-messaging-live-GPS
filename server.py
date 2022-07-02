#!/usr/bin/env python

# WS server example

import asyncio
from http import client
from numpy import true_divide
import websockets
from telethon import TelegramClient, events, Button
from telethon.tl.types import InputMessagesFilterPhotos
import json
from math import asin, cos, radians, sin, sqrt
import sqlite3
import paho.mqtt.client as mqtt
from datetime import datetime
# Use your own values from my.telegram.org
api_id = 4565522 
api_hash = '5eb30a5a061175e5fe84f325afdda5e8'
msgId = []
phNo = []
drivers = [['918078706253', 40.712776, -74.005974],
            ['918590939103', 41.712776, -74.005974],
            ['919847809874', 41.712776, -70.005974],
            ['917034487669', 31.712776, -70.005974],
            ['918111948462', 21.712776, -70.005974],
            ['918078205315', 31.712776, 70.005974],
            ['918589947708', 21.712776, 70.005974]]
client = TelegramClient('anon', api_id, api_hash)
mqttc = mqtt.Client(transport="websockets")
mqttc.connect("test.mosquitto.org", 8080, 60)


def dist_between_two_lat_lon(*args):
    lat1, lat2, long1, long2 = map(radians, args)

    dist_lats = abs(lat2 - lat1) 
    dist_longs = abs(long2 - long1) 
    a = sin(dist_lats/2)**2 + cos(lat1) * cos(lat2) * sin(dist_longs/2)**2
    c = asin(sqrt(a)) * 2
    radius_earth = 6378 # the "Earth radius" R varies from 6356.752 km at the poles to 6378.137 km at the equator.
    return c * radius_earth

def find_closest_lat_lon(data, v):
    try:
        return min(data, key=lambda p: dist_between_two_lat_lon(v[0],p[1],v[1],p[2]))
    except TypeError:
        print('Not a list or not a number.')

async def hello(websocket):
    with open('speaker.png', 'wb') as f:
        details = await websocket.recv()
        image = await websocket.recv()
        confirm = await websocket.recv()
        f.write(image)
        f.close()
    #print(f"< {name}")
    confirm = confirm.decode('utf-8')
    if confirm == "1":
        print(type(details))
        details = json.loads(details)
        try:
            await telegram(details,image)
        except:
            pass
    greeting = "received!"
    await websocket.send(greeting)
    print(f"> {greeting}")
async def telegram(details,image):
    conn  = sqlite3.connect('accident.db')
    cur = conn.cursor()
    capt = f"{details['NAME']}, {details['ADRESS']} met with an ACCIDENT at  https://www.google.com/maps/search/?api=1&query={details['GPS'][0]},{details['GPS'][1]}"
    NAME = details['NAME']
    msgId.clear()
    phNo.clear()
    with sqlite3.connect('accident.db', uri=True) as conn:
        cur = conn.cursor()
        cur.execute(f'SELECT EXISTS(SELECT 1 FROM LOG WHERE MESSAGE=? LIMIT 1)',(capt,))
        r = cur.fetchone()
        conn.commit()
   
    if r[0]==0:
        for i in range(1,4):
            msg = await client.send_file(details[f'NO{i}'],file = image,caption=capt)
            msgId.append(msg.id)
            phNo.append(details[f'NO{i}'])
        gps = []
        drivers_find = drivers.copy() 
        for i in range(0,3):
            gps.append(find_closest_lat_lon(drivers_find, details['GPS']))
            drivers_find.remove(gps[i])  
            phNo.append(gps[i][0])
            msg = await client.send_file(gps[i][0],image,caption=capt)
            msgId.append(msg.id)
        print(msgId)
        print(f"             The name is        :{NAME}")
        with sqlite3.connect('accident.db', uri=True) as conn:
            cur = conn.cursor()
            cur.execute('''INSERT INTO LOG VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(capt,phNo[0],phNo[1],phNo[2],phNo[3],phNo[4],phNo[5],msgId[0],msgId[1],msgId[2],msgId[3],msgId[4],msgId[5],0,'',0,0,NAME))
            conn.commit()
    
    else:
        print('message exist')
    conn.commit()
async def geo(ids, phone):
    #global ids

    message = await client.get_messages(phone, ids=ids)
    if message != None and message.geo!=None :
        await asyncio.sleep(10)
        print(message.geo)
        with sqlite3.connect('accident.db', uri=True) as conn:
            cur = conn.cursor()
            cur.execute('UPDATE DRIVER SET LATITUDE=?,LONGITUDE=?,MESSAGE_ID=? WHERE PHONE=?',(message.geo.long,message.geo.lat, int(ids), phone))
            conn.commit()
            

@client.on(events.UserUpdate)
async def update(event):
    print(event)
    print(event.geo)
	
@client.on(events.NewMessage)
async def handler(event):
    #replied = await event.get_message()
    global ids
    ids = event.id
    sender = await event.get_sender()
    try:
        phone = sender.phone
        await geo(ids, phone)
    except:
        pass
        
    if event.is_reply:
        if 'Accepted' or 'accepted' or 'ACCEPTED' in event.raw_text:
            conn  = sqlite3.connect('accident.db')
            cur = conn.cursor()
            replied = await event.get_reply_message()
            with sqlite3.connect('accident.db', uri=True) as conn:
                cur = conn.cursor()
                cur.execute('SELECT * FROM LOG WHERE MESSAGE=? LIMIT 1',(replied.text,))
                r = cur.fetchone()
            
           
            if(r!=None):
                if(int(r[13])==0):
                    sender = await event.get_sender()
                    await event.reply(f'You have accepted {r[0]}, Best wishes')
                    #print(sender.phone)
                    #print(sender.first_name)
                    msg =f"{sender.first_name} {sender.last_name} {sender.phone} have accepted {r[0]}"
                    msg1 = f'You have accepted {r[0]}, Best wishes'
                    with sqlite3.connect('accident.db', uri=True) as conn:
                        cur = conn.cursor()
                        cur.execute('UPDATE LOG SET STATUS=?,ACCEPTED_DRIVER=? , ACCEPTED_DRIVER_PH=?, TIME=? WHERE MESSAGE=?',(1,msg,sender.phone, datetime.now(), replied.text))
                        cur.execute('UPDATE DRIVER SET ACCIDENT=? WHERE PHONE=?',(r[17],sender.phone))
                        conn.commit()
                        
                    if  sender.phone !=r[1]:
                        await client.send_message(entity=r[1],message=msg, reply_to=int(r[1+6]))
                    if  sender.phone !=r[2]:
                        await client.send_message(entity=r[2],message=msg, reply_to=int(r[2+6]))
                    if  sender.phone !=r[3]:
                        await client.send_message(entity=r[3],message=msg, reply_to=int(r[3+6]))
                    if  sender.phone !=r[4]:
                        await client.send_message(entity=r[4],message=msg, reply_to=int(r[4+6]))
                    if  sender.phone !=r[5]:
                        await client.send_message(entity=r[5],message=msg, reply_to=int(r[5+6]))
                    if  sender.phone !=r[6]:
                        await client.send_message(entity=r[6],message=msg, reply_to=int(r[6+6]))
                       
                    #print(replied.text)
                else:
                    await event.reply(f'it is aldready choosen by {r[14]}')
                async for message in client.iter_messages(None,search =replied.text):
                    print(message.text)
            
async def update_gps():
    while True:
        with sqlite3.connect('accident.db', uri=True) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM DRIVER")
            rows = cur.fetchall()
            
        #cur.execute('SELECT * FROM LOG WHERE TIME > ?'),(datetime('now','-24 hour'),)
        #driver = cur.fetchall()
        
        for row in rows:
            #print(row)
            try:
                message = await client.get_messages(row[2], ids=row[3])

                if message != None and message.geo != None:
                    name_topic = f"{row[6]}\\name"
                    latitude_topic = f"{row[6]}\\latitude"
                    longitude_topic = f"{row[6]}\\longitude"
                    #print(latitude_topic)
                    mqttc.publish(latitude_topic, payload=row[4], qos=0, retain=False)
                    mqttc.publish(longitude_topic, payload=row[5], qos=0, retain=False)
                    mqttc.publish(name_topic, payload=row[1], qos=0, retain=False)
                with sqlite3.connect('accident.db', uri=True) as conn:
                    cur = conn.cursor()
                    c = conn.cursor()
                    cur.execute('UPDATE DRIVER SET LATITUDE=?,LONGITUDE=?,MESSAGE_ID=? WHERE PHONE=?',(message.geo.long,message.geo.lat, int(ids)))
                    conn.commit()
                    
            except:
                pass
        await asyncio.sleep(2)

async def server():
    await client.start()
    start_server = await websockets.serve(hello, 'localhost', 8765)
    await start_server.wait_closed()

async def main():
    f1 = loop.create_task(update_gps())
    f2 = loop.create_task(server())
    await asyncio.wait([f2,f1])
if __name__=="__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
    #asyncio.get_event_loop().run_until_complete(start_server)
    #asyncio.get_event_loop().run_forever()
