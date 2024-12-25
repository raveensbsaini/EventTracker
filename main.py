import struct
import time
import subprocess, shlex
import asyncio
import aiofiles
import sys
from databases import Database
import os
import functions
import pyautogui
from platformdirs import PlatformDirs

app_name = "EventTracker"
app_author = "Ravindra kumar saini"

dirs = PlatformDirs(app_name, app_author)
print("user_data_dir",dirs.user_data_dir)
data_dirs = dirs.user_data_dir
os.makedirs(data_dirs, exist_ok=True)

filepath_database = os.path.join(data_dirs,"database.db")
print(filepath_database)

list_of_events = functions.find_event()
database_uri = "sqlite+aiosqlite:///"+filepath_database
print(database_uri)
database = Database(database_uri)
print("start from begining")


async def create_database():
    await database.execute(
        'CREATE TABLE IF NOT EXISTS "events"("id" INTEGER PRIMARY KEY AUTOINCREMENT,"name" TEXT NOT NULL ,"event_key" INTEGER NOT NULL,"event_value" INTEGER NOT NULL,"time" REAL NOT NULL);'
    )
    await database.execute(
        'CREATE TABLE IF NOT EXISTS "window_titles"("id" INTEGER PRIMARY KEY AUTOINCREMENT,"name" TEXT NOT NULL,"time" REAL NOT NULL);'
    )
    await database.execute(
        'CREATE TABLE IF NOT EXISTS "screenshots"("id" INTEGER PRIMARY KEY AUTOINCREMENT,"location" TEXT NOT NULL,"time" REAL NOT NULL)'
    )


async def input(name, eventx):
    global database
    print("starting input",name,eventx)
    filepath = f"/dev/input/event{eventx}"
    event_format = "llHHI"
    bytes_size = struct.calcsize(event_format)
    async with aiofiles.open(
        filepath, "rb"
    ) as file:  # this is upper because(time taking)
        print("opened file")
        while True:
            try:
                byte_array = await file.read(bytes_size)
                print(byte_array)
                if byte_array:
                    (tv_sec, tv_usec, ev_type, ev_code, ev_value) = struct.unpack(
                        event_format, byte_array
                    )
                    timestamp = (
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tv_sec))
                        + f".{tv_usec:06d}"
                    )
                    await databae.connect()
                    async with database.transaction():
                        query = f"INSERT INTO  events(name,event_key,event_value,time) VALUES(:name,:event_key,:event_value,:time)"
                        values = {
                            "name": name,
                            "event_key": ev_code,
                            "event_value": ev_value,
                            "time": time.time(),
                        }
                        await database.execute(query=query, values=values)
                        print("saved to database")
                    await database.disconnect()
                else:
                    break
            except Exception as e:
                raise e


async def window():
    while True:
        cmd = "xprop -id $(xprop -root _NET_ACTIVE_WINDOW | cut -d ' ' -f 5) WM_NAME"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        try:
            async with database.transaction():
                query = "INSERT INTO window_titles(name,time) VALUES(:name,:time);"
                values = {"name": result.stdout, "time": time.time()}
                await database.execute(query=query, values=values)
            await asyncio.sleep(10)
        except Exception as e:
            raise e
async def screenshot():
    try:
        current_path = os.getcwd()
        while True:
            current_time = time.time()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            if os.path.exists(current_path + "/screenshots"):
                pass
            else:
                os.mkdir("./screenshots")
            file_path = os.getcwd() + "/screenshots/" + f"{timestamp}.png"
            a = pyautogui.screenshot(file_path)
            a.save(file_path)
            async with database.transaction():
                query = 'INSERT INTO "screenshots"("location","time") VALUES(:location,:time);'
                values = {"time":current_time,"location": file_path}
                await database.execute(query=query,values = values)
            await asyncio.sleep(10)
    except Exception as e:
        raise e


async def main():
    await create_database()
    task_list = [
        asyncio.create_task(input(name, eventx)) for name, eventx in list_of_events
    ]
    task_list.append(asyncio.create_task(window()))
    task_list.append(asyncio.create_task(screenshot()))
    await asyncio.gather(*task_list)
    await database.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
