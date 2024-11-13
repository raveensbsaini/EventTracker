from logging import _nameToLevel
import struct    
import time
import subprocess,shlex
import asyncio
import aiofiles
import sys
from databases import Database
import functions
database = Database('sqlite+aiosqlite:///database.db')
list_of_events = functions.find_event()
print(list_of_events)
  
async def input(name,eventx):
    print("listening to event",eventx)
    filepath = f"/dev/input/event{eventx}"
    event_format = "llHHI"
    bytes_size = struct.calcsize(event_format)
    count = 0

    async with aiofiles.open(filepath,"rb") as file:
        while True:
            byte_array  = await file.read(bytes_size)
            if byte_array:
                (tv_sec, tv_usec, ev_type, ev_code, ev_value) = struct.unpack(event_format, byte_array) 
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tv_sec)) + f".{tv_usec:06d}"
                print(f"Time: {timestamp}, Type: {ev_type}, Code: {ev_code}, Value: {ev_value}")
                if ev_type == 1: # I am bit sure does i still check it
                        async with database.transaction():
                            query = "INSERT INTO  keypress(name,event_key,event_value,time) as (:event_key,:event_value,timestamp)"
                            values = {"event_key":ev_code,"event_value":ev_value,"time":time.time()}
                            await database.execute(query=query,values=values)    
            else:
                print("========== didn't got byte_array")
                break
    print("add keyboard function ends")
async def window():
    print("window function starts")
    # after 10 second check window title
    while True:
        cmd = "xprop -id $(xprop -root _NET_ACTIVE_WINDOW | cut -d ' ' -f 5) WM_NAME"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        async with database.transaction():
            query="insert into windows_title(title,)"
        await asyncio.sleep(10)
async def main():
    await asyncio.gather(*[input(name,eventx) for name,eventx in list_of_events ])
asyncio.run(main())
