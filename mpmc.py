#!/usr/bin/env python3
import argparse
import asyncio
from datetime import datetime
from nio import (AsyncClient, RoomMessageText)
import os
import subprocess
import time


async def handle_message(room, event):
    roompath = os.path.join(args['dir'], args['server'], args['user'],
                            room.room_id)
    srcpath = os.path.join(roompath, event.sender)
    msgpath = os.path.join(srcpath, f"{event.event_id}:{args['server']}")
    timestamp = event.server_timestamp / 1000
    os.makedirs(srcpath, mode=0o700, exist_ok=True)
    with open(os.path.join(roompath, "name"), 'wt', encoding="utf-8") as f:
        f.write(room.display_name)
    with open(msgpath, 'wt', encoding="utf-8") as f:
        f.write(event.body)
    os.utime(msgpath, (timestamp, timestamp))
    print(msgpath, flush=True)


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
                        default='https://matrix.org',
                        help='homeserver')
    parser.add_argument('-d',
                        '--directory',
                        default=(os.environ.get('XDG_DATA_HOME')
                                 or os.path.expanduser('~/.local/share')) +
                        '/mm',
                        help='data storage directory')
    ns = parser.parse_args()
    password = subprocess.run(['sh', '-c', ns.pass_command],
                              stdout=subprocess.PIPE).stdout.decode('utf-8')
    return {
        'user': ns.user,
        'pass': password.rstrip('\n'),
        'server': ns.server.replace('https://', '', 1),
        'dir': ns.directory.rstrip('/')
    }


async def main():
    client = AsyncClient('https://' + args['server'], args['user'])
    client.add_event_callback(handle_message, RoomMessageText)
    await client.login(args['pass'])
    await client.sync_forever(timeout=30000)


args = get_args()
asyncio.get_event_loop().run_until_complete(main())
