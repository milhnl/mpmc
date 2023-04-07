#!/usr/bin/env python3
import aiofiles
import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
from nio import (AsyncClient, RoomMessageText)
import os


async def handle_message(room, event):
    roompath = os.path.join(clientdir, room.room_id)
    srcpath = os.path.join(roompath, event.sender)
    msgpath = os.path.join(srcpath, f"{event.event_id}:{args.server}")
    timestamp = event.server_timestamp / 1000
    os.makedirs(srcpath, mode=0o700, exist_ok=True)
    with open(os.path.join(roompath, "name"), 'wt', encoding="utf-8") as f:
        f.write(room.display_name)
    if not os.path.exists(msgpath):
        with open(msgpath, 'wt', encoding="utf-8") as f:
            f.write(event.body)
        os.utime(msgpath, (timestamp, timestamp))
        print(msgpath, flush=True)


async def send_message(room, text):
    await client.room_send(room_id=room.room_id,
                           message_type="m.room.message",
                           content={
                               "msgtype": "m.text",
                               "body": text
                           })


def fifo_listener(room, loop):
    roompath = os.path.join(clientdir, room.room_id)
    os.makedirs(roompath, mode=0o700, exist_ok=True)
    path = os.path.join(roompath, "in")
    try:
        os.remove(path)
    except OSError:
        pass
    os.mkfifo(path, mode=0o700)
    while True:
        with open(path, mode="r") as f:
            text = f.read().rstrip("\n")
            loop.create_task(send_message(room, text))


async def fifo_listener_proxy(room):
    io_pool_exc = ThreadPoolExecutor()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(io_pool_exc, lambda: fifo_listener(room, loop))


def get_args():
    parser = argparse.ArgumentParser(
        conflict_handler='resolve',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u',
                        '--user',
                        default=os.environ.get('USER'),
                        help='username')
    parser.add_argument('-p',
                        '--pass-command',
                        required=True,
                        help='command to run to get password')
    parser.add_argument('-s',
                        '--server',
                        required=True,
                        default='matrix.org',
                        type=lambda x: x.replace('https://', '', 1),
                        help='homeserver')
    parser.add_argument('-d',
                        '--directory',
                        default=os.path.join(
                            os.environ.get('XDG_DATA_HOME')
                            or os.path.expanduser('~/.local/share'), 'mpmc'),
                        type=lambda x: x.rstrip('/'),
                        help='data storage directory')
    return parser.parse_args()


async def do_subprocess(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    return stdout.decode('utf-8').rstrip('\n')


async def main():
    client.add_event_callback(handle_message, RoomMessageText)
    password = await do_subprocess(args.pass_command)
    await client.login(password)

    await client.sync()  #We need the list of rooms
    await asyncio.gather(
        client.sync_forever(timeout=500),
        *[fifo_listener_proxy(room) for room in client.rooms.values()],
        return_exceptions=True)


if __name__ == "__main__":
    args = get_args()
    client = AsyncClient('https://' + args.server, args.user)
    clientdir = os.path.join(args.directory, args.server, args.user)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(client.close())
        os._exit(1)  #To kill the other threads.
