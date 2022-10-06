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

import json
import discord
import os
import pickle
import numpy as np
from discord.channel import VoiceChannel
from discord.player import FFmpegPCMAudio
from google.cloud import texttospeech
from discord.ext import commands
from discord.channel import VoiceChannel
from dotenv import load_dotenv
load_dotenv(override=True)

TOKEN = os.environ['TOKEN']
EDEN_TOKEN = os.environ['EDEN_TOKEN']

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

voiceChannel: VoiceChannel 


from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def get_credentials(client_secret_file, scopes,
                    token_storage_pkl='token.pickle'):
    creds = None
    # token.pickleファイルにユーザのアクセス情報とトークンが保存される
    # ファイルは初回の認証フローで自動的に作成される
    if os.path.exists(token_storage_pkl):
        with open(token_storage_pkl, 'rb') as token:
            creds = pickle.load(token)

    # 有効なクレデンシャルがなければ、ユーザーにログインしてもらう
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_file, scopes=scopes)
            creds = flow.run_local_server(port=0)

        # クレデンシャルを保存（次回以降の認証のため）
        with open(token_storage_pkl, 'wb') as token:
            pickle.dump(creds, token)

    return creds


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

 # Instantiates a client
client = texttospeech.TextToSpeechClient()

# Set the text input to be synthesized
synthesis_input = texttospeech.SynthesisInput(message.content)

# Build the voice request, select the language code ("en-US") and the ssml
# voice gender ("neutral")
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
)

# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

# Perform the text-to-speech request on the text input with the selected
# voice parameters and audio file type
response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

# The response's audio_content is binary.
with open("output.mp3", "wb") as out:
    # Write the response to the output file.
    out.write(response.audio_content)
    print('Audio content written to file "output.mp3"')
   
 
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
