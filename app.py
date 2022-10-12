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
import discord
import json
import os
from gtts import gTTS
from dotenv import load_dotenv
from collections import defaultdict, deque
from pathlib import Path
from discord import Intents
from apiclient.discovery import build
from discord.player import FFmpegPCMAudio
from discord.channel import VoiceChannel
# .envファイルの内容を読み込見込む
load_dotenv()
TOKEN = os.environ['TOKEN']

from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.cloud import texttospeech
from google.oauth2 import service_account
from googleapiclient.discovery import build


intents: Intents = discord.Intents.all()
client = discord.Client(intents=intents)
voiceChannel: VoiceChannel 

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
         text = message.content
         if message.content == '!con':
            voiceChannel = await VoiceChannel.connect(message.author.voice.channel)
            await message.channel.send('読み上げるよ！')
            return
         if message.content == '!en':
            VoiceChannel.stop()
            await message.channel.send('またね！')
            await VoiceChannel.disconnect()
            return
         elif message.content != '!con' or '!en':
              from google.cloud import texttospeech
              client = texttospeech.TextToSpeechClient()
              synthesis_input = texttospeech.SynthesisInput(text=text)
              voice = texttospeech.VoiceSelectionParams(
                  language_code="ja-JP", 
                  ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
              )
              audio_config = texttospeech.AudioConfig(
                   audio_encoding=texttospeech.AudioEncoding.MP3
              )
              response = client.synthesize_speech(
                  input=synthesis_input, voice=voice, audio_config=audio_config
              )
              with open("hello.mp3", "wb") as out:
                  out.write(response.audio_content)
                  print('Audio content written to file "hello.mp3"')
                  message.guild.voice_client.play(discord.FFmpegPCMAudio("hello.mp3"))
         return

client.run(TOKEN)
            
