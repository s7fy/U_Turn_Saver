import discord
from discord.ext import commands
import os
import mysql.connector

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)

# MySQL接続情報
config = {
    'user': 'foo',
    'password': 'gaa',
    'host': 'hoge',
    'database': 'u_turn_saver',
    'port': 'bar'
}

# MySQLに接続
conn = mysql.connector.connect(**config)
cursor = conn.cursor(prepared=True)

# テーブルが存在しない場合は作成する
cursor.execute('''
    CREATE TABLE IF NOT EXISTS counters (
        channel_id VARCHAR(255) PRIMARY KEY,
        counter INT
    )
''')
conn.commit()

@client.event
async def on_ready():
    print('Bot is ready.')

@client.event
async def on_message(message):
    if message.channel.type == discord.ChannelType.text:
        channel_id = str(message.channel.id)

        # チャンネルごとのカウンターをデータベースから取得
        query = 'SELECT counter FROM counters WHERE channel_id = %s'
        params = (channel_id,)
        cursor.execute(query, params)
        result = cursor.fetchone()
        if result:
            counter = result[0]
        else:
            counter = 1

        channel_name = message.channel.name

        # チャンネル名に使用できない文字を削除してフォルダ名を作成
        folder_name = ''.join(c for c in channel_name if c.isalnum())

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        if message.attachments:
            # 添付された画像がある場合の処理
            for attachment in message.attachments:
                # 画像の拡張子を取得
                _, extension = os.path.splitext(attachment.filename)

                # 保存ファイル名を作成
                file_name = f'{counter}{extension}'

                # 画像をダウンロードして保存
                await attachment.save(f'{folder_name}/{file_name}')

                counter += 1
        elif message.content and len(message.attachments) == 0:
            # 画像単体の場合の処理
            for attachment in message.embeds:
                if isinstance(attachment, discord.Embed) and attachment.image.url:
                    # 画像のURLから拡張子を取得
                    _, extension = os.path.splitext(attachment.image.url)

                    # 保存ファイル名を作成
                    file_name = f'{counter}{extension}'

                    # 画像をダウンロードして保存
                    await attachment.image.save(f'{folder_name}/{file_name}')

                    counter += 1

        # チャンネルごとのカウンターの値をデータベースに保存
        replace_query = 'REPLACE INTO counters (channel_id, counter) VALUES (%s, %s)'
        params = (channel_id, counter)
        cursor.execute(replace_query, params)
        conn.commit()



client.run('Here is Discord API Token')

