import datetime
import asyncio
import os
import re

from datetime import timedelta
from datetime import time
from discord import Game
from discord.ext.commands import Bot

BOT_PREFIX = ("?", "!")
TOKEN = 'TOKEN HERE'
CHANNEL_ID = 'CHANNEL ID HERE'
FILE_NAME = 'Date.DBot'

timer_set = False
sent_warning = False
sent_reminder = False

timer = datetime.datetime.now()

client = Bot(command_prefix=BOT_PREFIX)

@client.command(name='SetMeeting',
                description="Sets reminders for next meeting. Syntax !Set_Meeting yyyy-mm-dd HH:MM",
                brief="Sets reminders for next meeting",
                aliases=['setmeeting', 'set_meeting','Set_Meeting','Set-Meeting', 'set-meeting'],
                pass_context=True)
async def set_meeting(ctx, *args):
    global timer, timer_set, sent_reminder, sent_warning

    if re.match('\d\d\d\d-\d\d-\d\d', args[0]) and re.match('\d\d:\d\d', args[1]):
        y, m, d = args[0].split("-")
        H, M = args[1].split(":")

        timer = datetime.datetime(int(y), int(m), int(d), int(H), int(M))
        if timer > datetime.datetime.now():
            print("Set date for next meeting to: " + timer.strftime("%Y-%m-%d %H:%M"))
            await client.say("Setting date for next meeting to: " + timer.strftime("%Y-%m-%d %H:%M"))

            timer_set = True
            sent_warning = False
            sent_reminder = False

            try:
                file = open(FILE_NAME, 'r')
                # read a list of lines into data
                data = file.readlines()
                file.close()

                data[0] = str(timer)

                file = open(FILE_NAME, 'w')
                file.writelines(data)
                file.close()

            except:
                file = open(FILE_NAME, 'w')
                file.write(str(timer))
                file.close()
        else:
            await client.say("Error: Please ensure date as not passed")
    else:
        await client.say("Syntax Error: Please ensure format !set_meeting yyyy-mm-dd HH:MM")



@client.event
async def on_ready():
    global timer_set
    await client.change_presence(game=Game(name="with time"))
    print("Logged in as " + client.user.name)

    try:
        file = open(FILE_NAME, 'r')
        # read a list of lines into data
        data = file.readlines()
        file.close()

        timer = data[0]

        timer_set = True
    except:
        pass



async def check_time():
    await client.wait_until_ready()
    global timer_set, sent_reminder, sent_warning
    t = time(12,00)
    print("Checking if timer is up")
    channel = client.get_channel(CHANNEL_ID)
    while not client.is_closed:
        if timer_set:
            if datetime.datetime.now() > timer - timedelta(0,0,0,0,5,0,0) and not sent_warning:
                await client.send_message(channel, "@everyone Möte om 30 min!")

                sent_warning = True
            elif datetime.datetime.now() > timer:
                await client.send_message(channel, "@everyone Mötet börjar nu! ")

                if os.path.isfile(FILE_NAME):
                    os.remove(FILE_NAME)
                timer_set = False
            elif datetime.datetime.now() > datetime.datetime.combine(timer.date(),t) and not sent_reminder:
                await client.send_message(channel, "@everyone Kom ihåg att det är möte idag:  " + timer.strftime("%Y-%m-%d %H:%M"))
                sent_reminder = True

        await asyncio.sleep(5)

client.loop.create_task(check_time())
client.run(TOKEN)