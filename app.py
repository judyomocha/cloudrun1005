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
from dotenv import load_dotenv
# .envファイルの内容を読み込見込む
load_dotenv()
TOKEN = os.environ['TOKEN']
GUILD_ID = os.environ['GUILD_ID']
CHANNEL_ID = os.environ['CHANNEL_ID']
SPREADSHEET_KEY = os.environ['SPREADSHEET_KEY']
GCP_SA_KEY = os.environ['GCP_SA_KEY']
SHEET_NAME = os.environ['SHEET_NAME']

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
parsed = json.loads(GCP_SA_KEY)
gc = gspread.service_account_from_dict(parsed)
sh = gc.open_by_key(SPREADSHEET_KEY)
ws = sh.worksheet(SHEET_NAME)


intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id != int(CHANNEL_ID):
        return

    if message.channel.id == int(CHANNEL_ID):
        data = message.content

        def next_available_row(ws):
            str_list = list(filter(None, ws.col_values(1)))
            return str(len(str_list) + 1)
        next_row = next_available_row(ws)

        ws.update_cell(next_row, 1, data)
        await message.channel.send(f'更新します {message.author}!') 
        
client.run(TOKEN)
