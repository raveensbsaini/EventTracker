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
import structlog


log = structlog.get_logger()
app_name = "EventTracker"
app_author = "Ravindra kumar saini"
log.info("Welcome to EventTracker",key="Starting the server")
dirs = PlatformDirs(app_name, app_author)

data_dirs = dirs.user_data_dir
try:
    os.makedirs(data_dirs, exist_ok=True)
except error as e:
    log.error("cannot create user_data_dir",e)
filepath_database = os.path.join(data_dirs,"database.db")

filepath_screenshots = os.path.join(data_dirs,"screenshots")
try:
    os.makedirs(filepath_screenshots,exist_ok = True)
    log.info(f"creating{filepath_screenshots}")
except error as e:
    log.erro(e)
print(filepath_screenshots)

list_of_events = functions.find_event()
database_uri = "sqlite+aiosqlite:///"+filepath_database
database = Database(database_uri)

async def create_database():
    try:
        await database.connect()
        log.info("checking for existing database. Creating if not found")
        await database.execute(
            'CREATE TABLE IF NOT EXISTS "events"("id" INTEGER PRIMARY KEY AUTOINCREMENT,"name" TEXT NOT NULL ,"event_key" INTEGER NOT NULL,"event_value" INTEGER NOT NULL,"time" REAL NOT NULL);'
        )
        await database.execute(
            'CREATE TABLE IF NOT EXISTS "window_titles"("id" INTEGER PRIMARY KEY AUTOINCREMENT,"name" TEXT NOT NULL,"time" REAL NOT NULL);'
        )
        await database.execute(
            'CREATE TABLE IF NOT EXISTS "screenshots"("id" INTEGER PRIMARY KEY AUTOINCREMENT,"location" TEXT NOT NULL,"time" REAL NOT NULL)'
        )
        log.info("database stored")
        await database.disconnect()
    except:
        log.error("database isn't created",value = "create_database function")


async def input(name, eventx):
    log.info("input event",key = name,eventx = eventx)
    global database
    await database.connect()
    filepath = f"/dev/input/event{eventx}"
    event_format = "llHHI"
    bytes_size = struct.calcsize(event_format)
    async with aiofiles.open(
        filepath, "rb"
    ) as file:  # this is upper because(time taking)
        
        while True:
            try:
                byte_array = await file.read(bytes_size)
                if byte_array:
                    (tv_sec, tv_usec, ev_type, ev_code, ev_value) = struct.unpack(
                        event_format, byte_array
                    )
                    timestamp = (
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tv_sec))
                        + f".{tv_usec:06d}"
                    )
                    async with database.transaction():
                        query = f"INSERT INTO  events(name,event_key,event_value,time) VALUES(:name,:event_key,:event_value,:time)"
                        values = {
                            "name": name,
                            "event_key": ev_code,
                            "event_value": ev_value,
                            "time": time.time(),
                        }
                        await database.execute(query=query, values=values)
                        log.info("stored input in database")
                        
                    
                else:
                    log.warning("cannot stored in database")
                    break
            except Exception as e:
                log.error(e,key="in exception")
                raise e
    await database.disconnect()

async def window():
    while True:
        cmd = "xprop -id $(xprop -root _NET_ACTIVE_WINDOW | cut -d ' ' -f 5) WM_NAME"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        try:
            async with database.transaction():
                query = "INSERT INTO window_titles(name,time) VALUES(:name,:time);"
                values = {"name": result.stdout, "time": time.time()}
                await database.execute(query=query, values=values)
                log.info("window title captured",key = result.stdout)
            await asyncio.sleep(10)
        except Exception as e:
            log.error(e)
            raise e
async def screenshot():
    global filepath_screenshots
    try:
        while True:
            current_time = time.time()
            print(current_time)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            a = pyautogui.screenshot()
            a.save(filepath_screenshots+f"/{timestamp}.png")
            async with database.transaction():
                query = 'INSERT INTO "screenshots"("location","time") VALUES(:location,:time);'
                values = {"time":current_time,"location": filepath_screenshots}
                await database.execute(query=query,values = values)
                log.info("screenshot saved",location = filepath_screenshots)
            await asyncio.sleep(10)
    except Exception as e:
        log.error("cannot saved screenshot",error = e)
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
