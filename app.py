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
import discord
import json
import os
from dotenv import load_dotenv
# .envファイルの内容を読み込見込む
load_dotenv()
TOKEN = os.environ['TOKEN']


intents: Intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('Login!!!')


@client.event
@client.event
async def on_message(message):
    global voiceChannel
    if message.author.bot:
        return
    if message.author.voice.channel:
        if message.content == '!con':
            voiceChannelｌ = await VoiceChannel.connect(message.author.voice.channel)
            await message.channel.send('読み上げるよ！')
            return
        if message.content == '!en':
            VoiceChannel.stop()
            await message.channel.send('またね！')
            await VoiceChannel.disconnect()
            return
        elif message.content != '!con' or '!en':
            tts = gTTS(message.content)
            tts.save("hello.mp3")
            message.guild.voice_client.play(discord.FFmpegPCMAudio("hello.mp3"))
            return
    else:
        return


client.run(TOKEN)
