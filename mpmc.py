#!/usr/bin/env python3
import argparse
import asyncio
from nio import (AsyncClient, RoomMessageText)
import os
import subprocess


async def message_cb(room, event):
    print("Message received for room {} | {}: {}".format(
        room.display_name, room.user_name(event.sender), event.body))


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
    parser.add_argument('-h',
                        '--homeserver',
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
        'homeserver': ns.homeserver.replace('https://', '', 1),
        'dir': ns.directory.rstrip('/')
    }


async def main():
    client = AsyncClient('https://' + args['homeserver'], args['user'])
    client.add_event_callback(message_cb, RoomMessageText)
    await client.login(args['pass'])
    await client.sync_forever(timeout=30000)


args = get_args()
asyncio.get_event_loop().run_until_complete(main())
