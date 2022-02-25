import asyncio
import os
from typing import Optional
import discord
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
import mysql.connector
from datetime import datetime
load_dotenv()

db = mysql.connector.connect(
    host = getenv('DB_HOST'),
    user = getenv('DB_USER'),
    passwd = getenv('DB_PASS'),
    database = "member_db"
    )

mycursor = db.cursor(buffered=True)

class JoinLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        id = int(member.id)
        mycursor.execute("SELECT id FROM members WHERE id = %(id)s", {'id': id})
        checkIdExists = mycursor.fetchone()
        if checkIdExists == None:
            user = str(member.display_name)

            mycursor.execute("SELECT id FROM roles ORDER BY id DESC")
            num = mycursor.fetchone()
            limit = num[0]
            
            mycursor.execute("SELECT role FROM roles WHERE id = %(id)s", {'id': limit})
            roleName = mycursor.fetchone()
            role = discord.utils.get(member.guild.roles, name = roleName[0])
            
            while role not in member.roles and limit > 0:
                mycursor.execute("SELECT role FROM roles WHERE id = %(id)s", {'id' : limit})
                roleName = mycursor.fetchone()
                role = discord.utils.get(member.guild.roles, name=roleName[0])
                limit = limit - 1

            if role in member.roles:
                mycursor.execute("INSERT INTO members(id, name, role) VALUES (%s, %s, %s)", (id, user, str(role)))
                
            else:
                mycursor.execute("INSERT INTO members(id, name) VALUES (%s, %s)", (id, user))
        db.commit()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        id = int(member.id)
        mycursor.execute("SELECT id FROM members WHERE id = %(id)s", {'id' : id})
        checkIdExists = mycursor.fetchone()
        if checkIdExists != None:
            mycursor.execute("DELETE FROM members WHERE id = %(id)s", {'id' : id})
        db.commit()
        

def setup(bot):
    bot.add_cog(JoinLeave(bot))
    print("database check")        