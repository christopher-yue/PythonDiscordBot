import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
import mysql.connector
from datetime import datetime
load_dotenv()


db = mysql.connector.connect(
    host=getenv('DB_HOST'),
    user=getenv('DB_USER'), 
    passwd=getenv('DB_PASS'),
    database = "member_db"
)

mycursor = db.cursor(buffered=True)
#mycursor.execute("CREATE TABLE members(id bigint PRIMARY KEY, name VARCHAR(50), role ENUM('admin', 'mod'))")
#mycursor.execute("DROP TABLE members")
#mycursor.execute("CREATE TABLE roles(id int PRIMARY KEY AUTO_INCREMENT, role VARCHAR(50), role_id BIGINT(18))")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

#---connect cogs---
@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
#------

@bot.event
async def on_ready():
    print("Bot is online!")

bot.run(getenv('BOT_TOKEN'))