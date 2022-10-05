# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import signal
import sys
from types import FrameType
from flask import Flask
from utils.logging import logger
app = Flask(__name__)
from google.oauth2.service_account import Credentials
import gspread
import discord
import json
import os
import traceback
import hmac
import hashlib
import requests
from discord.ext import commands
from discord.player import FFmpegPCMAudio
from io import BytesIO

TOKEN = os.environ['TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']
SPREADSHEET_KEY = os.environ['SPREADSHEET_KEY']
GCP_SA_KEY = os.environ['GCP_SA_KEY']
SHEET_NAME = os.environ['SHEET_NAME']
COEFONT_KEY = os.environ['COEFONT_KEY']
COEFONT_SECRET = os.environ['COEFONT_SECRET']


scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
parsed = json.loads(GCP_SA_KEY)
gc = gspread.service_account_from_dict(parsed)
sh = gc.open_by_key(SPREADSHEET_KEY)
ws = sh.worksheet(SHEET_NAME)
list_of_lists = ws.get_all_values()
i = len(list_of_lists[0])

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!')


@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command(name='join')
async def cmd_join(ctx):
    if ctx.message.guild:
        if ctx.author.voice is None:
            pass
        elif ctx.guild.voice_client:
            await ctx.guild.voice_client.move_to(ctx.author.voice.channel)
            await ctx.send('move vc')
        else:
            await ctx.author.voice.channel.connect()
            await ctx.send('join vc')


@bot.command(name='dc')
async def cmd_dc(ctx):
    if ctx.message.guild:
        if ctx.voice_client is None:
            pass
        else:
            await ctx.voice_client.disconnect()


@bot.command(name='cf')
async def cmd_coefont(ctx, *args):

    if len(args) <= 0:
        await ctx.send('入力文字数が不正です（1~100)')
        return

    arguments = ', '.join(args)
    if len(arguments) < 100:
        if ctx.message.guild.voice_client:
            coefontTTS(ctx, arguments)
    else:
        await ctx.send('入力文字数が不正です（1~100)')


def coefontTTS(ctx, text):
    signature = hmac.new(bytes(CF_SECRET, 'utf-8'), text.encode('utf-8'), hashlib.sha256).hexdigest()
    url = 'https://api.coefont.cloud/text2speech'
    response = requests.post(url, data=json.dumps({
        'coefont': 'Averuni',
        'text': text,
        'accesskey': CF_KEY,
        'signature': signature
    }), headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        with open('tts.wav', 'wb') as f:
            f.write(response.content)
            ctx.guild.voice_client.play(FFmpegPCMAudio('tts.wav'))


bot.run(TOKEN)



@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id != int(CHANNEL_ID):
        return

    if message.channel.id == int(CHANNEL_ID):
        ws.update_cell(i+1,1,message.content )
        print(f'更新します @{message.author}!') 
        await message.channel.send(f'更新します {message.author}!') 

client.run(TOKEN)
