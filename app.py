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
import json
import os
import traceback
import hmac
import hashlib
import requests
import discord
import html
from google.cloud import speech
from discord.channel import VoiceChannel
from discord.player import FFmpegPCMAudio
from google.cloud import texttospeech
from discord.ext import commands
from discord.channel import VoiceChannel

TOKEN = os.environ['TOKEN']
GCP_SA_KEY = os.environ['GCP_SA_KEY']

parsed = json.loads(GCP_SA_KEY)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

voiceChannel: VoiceChannel 

@client.event
async def on_ready():
    print('Login!!!')

@client.event
async def on_message(message):
    global voiceChannel

    if message.author.bot:
        return
    if message.content == '!connect':
        voiceChannel = await VoiceChannel.connect(message.author.voice.channel)
        await message.channel.send('読み上げBotが参加しました')
        return
    elif message.content == '!disconnect':
        voiceChannel.stop()
        await message.channel.send('読み上げBotが退出しました')
        await voiceChannel.disconnect()
        return

    play_voice(message.content)

def text_to_ssml(text):
    escaped_lines = html.escape(text)
    ssml = "{}".format(
        escaped_lines.replace("\n", '\n<break time="1s"/>')
    )
    return ssml

def ssml_to_speech(ssml, file, language_code, gender):
    ttsClient = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=ssml)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code, ssml_gender=gender
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = ttsClient.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(file, "wb") as out:
        out.write(response.audio_content)
        print("Audio content written to file " + file)
    return file

def play_voice(text):
    ssml = text_to_ssml(text)
    file = ssml_to_speech(ssml, "voice.mp3", "ja-JP", texttospeech.SsmlVoiceGender.MALE)
    voiceChannel.play(FFmpegPCMAudio(file))

client.run(TOKEN)
