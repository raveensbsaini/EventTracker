import struct    
import time
import subprocess,shlex
import asyncio
import aiofiles
import sys
from databases import Database
import functions
list_of_events = functions.find_event()
database = Database('sqlite+aiosqlite:///database.db')
async def create_database():
    await database.execute('CREATE TABLE IF NOT EXISTS "events"("id" INTEGER PRIMARY KEY AUTOINCREMENT,"name" TEXT NOT NULL ,"event_key" INTEGER NOT NULL,"event_value" INTEGER NOT NULL,"time" REAL NOT NULL);')
    await database.execute('CREATE TABLE IF NOT EXISTS "window_titles"("id" INTEGER PRIMARY KEY AUTOINCREMENT,"name" TEXT NOT NULL,"time" REAL NOT NULL);')
async def input(name,eventx):
    filepath = f"/dev/input/event{eventx}"
    event_format = "llHHI"
    bytes_size = struct.calcsize(event_format)
    async with aiofiles.open(filepath,"rb") as file:# this is upper because(time taking)
        while True:
            try:
                byte_array  = await file.read(bytes_size)
                if byte_array:
                    (tv_sec, tv_usec, ev_type, ev_code, ev_value) = struct.unpack(event_format, byte_array) 
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tv_sec)) + f".{tv_usec:06d}"
                    print(f"Time: {timestamp}, Type: {ev_type}, Code: {ev_code}, Value: {ev_value}")
                    async with database.transaction():    
                        query = f"INSERT INTO  events(name,event_key,event_value,time) VALUES(:name,:event_key,:event_value,:time)"
                        values = {"name":name,"event_key":ev_code,"event_value":ev_value,"time":time.time()}
                        await database.execute(query=query,values=values)                        
                else:
                    break
            except Exception as e:
                print(e)
                return None
async def window():
    while True:
        cmd = "xprop -id $(xprop -root _NET_ACTIVE_WINDOW | cut -d ' ' -f 5) WM_NAME"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        try:
            async with database.transaction():
                query="INSERT INTO window_titles(name,time) VALUES(:name,:time);"
                values = {"name":result.stdout,"time":time.time()}
                await database.execute(query=query,values=values)
            await asyncio.sleep(10)
        except Exception as e:
            print("exception",e)
            return None
async def screenshot():
    while True:
        pass
async def main():
    await create_database()
    task_list = [asyncio.create_task(input(name,eventx)) for name,eventx in list_of_events]
    task_list.append(asyncio.create_task(window()))
    await asyncio.gather(*task_list)
    await database.disconnect()
if __name__ == "__main__":
    asyncio.run(main())
