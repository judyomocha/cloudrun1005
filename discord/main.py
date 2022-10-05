import gspread
import discord
import json
# 必要モジュールのインポート
import os
from dotenv import load_dotenv
from google.cloud import storage
# .envファイルの内容を読み込見込む
load_dotenv()
from oauth2client.service_account import ServiceAccountCredentials
TOKEN = os.environ['TOKEN']
FILENAME = os.environ['FILENAME']
#jsonファイルを使って認証情報を取得
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

def explicit():
    from google.cloud import storage

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json(
        CREDENTIALS)

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    print(buckets)
credentials = ServiceAccountCredentials.from_json_keyfile_name(FILENAME, scope)
gc = gspread.authorize(credentials)

#共有したスプレッドシートのキー（後述）を使ってシートの情報を取得
workbook = gs.open_by_key('174aQ9OHuElBLrTLhidRCoux6V0c1NXBl3zJBifILTf4')
print(worksheet.acell("G2").value)

guild_id = 1004213987757527142
channel_id = 1022872755642826824

async def greeting():
    greet = client.get_channel(channel_id)
    await greet.send('こんにちは！')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):

    #メッセージを送ったのがBot自身であるときは何もしない。
    if message.author == client.user:
        return
    #「!exit」と入力すると終了する
    if message.channel.id == channel_id:
        await message.channel.send('別にいいやん')
    #他の時は送ったメッセージに対して反応してくれる
    if message.channel.id != channel_id:
        return      
    else:
        return

@client.event
async def on_message(message):  # メッセージを受け取ったときの挙動
    if message.author.bot:  # Botのメッセージは除く
        return
    print(message.content)
    worksheet_list = workbook.worksheets()
    #　1つ目のシートのセル(1,1)をDiscordに送ったメッセージ内容で更新
    worksheet_list[0].update_cell(1, 1, message.content)


client.run(TOKEN)