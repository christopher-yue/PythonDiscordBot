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

class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #CLEAR
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, limit: Optional[int] = 1):
        with ctx.channel.typing():
            await ctx.message.delete()
            deleted = await ctx.channel.purge(limit = limit)
            await ctx.send(f"Deleted `" + str(len(deleted)) + "` messages", delete_after=3)

    #ADD MEMBERS
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addm(self, ctx, member: discord.Member):
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
            role = discord.utils.get(ctx.guild.roles, name = roleName[0])
            
            while role not in member.roles and limit > 0:
                mycursor.execute("SELECT role FROM roles WHERE id = %(id)s", {'id' : limit})
                roleName = mycursor.fetchone()
                role = discord.utils.get(ctx.guild.roles, name=roleName[0])
                limit = limit - 1

            if role in member.roles:
                await ctx.send(id)
                await ctx.send(user)
                await ctx.send(role)
                mycursor.execute("INSERT INTO members(id, name, role) VALUES (%s, %s, %s)", (id, user, str(role)))
                
            else:
                mycursor.execute("INSERT INTO members(id, name) VALUES (%s, %s)", (id, user))
        else:
            await ctx.send("Member has already been added")
        db.commit()
        
    #DROP MEMBERS
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def dropm(self, ctx, member: discord.Member=None):
        id = int(member.id)
        mycursor.execute("SELECT id FROM members WHERE id = %(id)s", {'id' : id})
        checkIdExists = mycursor.fetchone()
        if checkIdExists != None:
            mycursor.execute("DELETE FROM members WHERE id = %(id)s", {'id' : id})
            await ctx.send("Member has been removed")
            db.commit()
        else:
            await ctx.send("Member does not exist")


    #ADD ROLES
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addr(self, ctx, roleName):
        mycursor.execute("SELECT role FROM roles WHERE role = %(role)s", {'role' : roleName})
        checkRoleExists = mycursor.fetchone()
        if checkRoleExists == None:
            if discord.utils.get(ctx.guild.roles, name=roleName):
                role = discord.utils.get(ctx.guild.roles, name=roleName)
                await ctx.send(role.id)
                mycursor.execute("INSERT INTO roles(role, role_id) VALUES(%s, %s)", (str(role), int(role.id)))
                await ctx.send("Role has been added")
                db.commit()
            else:
                await ctx.send("Role doesn't exist")
        else:
            await ctx.send("Role has already been added")
        
    #UPDATE ROLES
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def updater(self, ctx, oldRole, newRole):
        mycursor.execute("SELECT role FROM roles WHERE role = %(role)s", {'role' : oldRole})
        checkOldRoleExists = mycursor.fetchone()
        mycursor.execute("SELECT role FROM roles WHERE role = %(role)s", {'role' : newRole})
        checkNewRoleExists = mycursor.fetchone()
        if checkOldRoleExists != None and checkNewRoleExists == None:
            if discord.utils.get(ctx.guild.roles, name=newRole):
                role = discord.utils.get(ctx.guild.roles, name=newRole)
                
                oldRole = discord.utils.get(ctx.guild.roles, name=oldRole)
                mycursor.execute("UPDATE roles SET role = %s WHERE role_id = %s", (str(role), oldRole.id))
                mycursor.execute("UPDATE roles SET role_id = %s WHERE role_id = %s", (role.id, oldRole.id))
                await ctx.send("Role has been updated")
                await ctx.send(str(role) + "(" + str(role.id) + ") was " + str(oldRole) + "(" + str(oldRole.id) + ")")
                db.commit()
            else:
                await ctx.send("New role doesn't exist")
        else:
            if checkOldRoleExists == None:
                await ctx.send("Old role doesn't exist")
            else:
                await ctx.send("New role already exists")
        db.commit()    

    #UPDATE MEMBERS
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def updatem(self, ctx, member: discord.Member=None):
        id = int(member.id)
        mycursor.execute("SELECT id FROM members WHERE id = %(id)s", {'id' : id})
        checkIdExists = mycursor.fetchone()
        if checkIdExists != None:
            user = str(member.display_name)
            mycursor.execute("SELECT id FROM roles ORDER BY id DESC")
            num = mycursor.fetchone()
            limit = num[0]
            
            mycursor.execute("SELECT role FROM roles WHERE id = %(id)s", {'id': limit})
            roleName = mycursor.fetchone()
            role = discord.utils.get(ctx.guild.roles, name = roleName[0])
            
            while role not in member.roles and limit > 0:
                mycursor.execute("SELECT role FROM roles WHERE id = %(id)s", {'id' : limit})
                roleName = mycursor.fetchone()
                role = discord.utils.get(ctx.guild.roles, name=roleName[0])
                limit = limit - 1

            if role in member.roles:
                await ctx.send(id)
                await ctx.send(user)
                await ctx.send(role)
                mycursor.execute("UPDATE members SET role = %s WHERE id = %s", (str(role), id))
            else:
                await ctx.send("No roles")
            
            mycursor.execute("UPDATE members SET name = %s WHERE id = %s", (user, id))
            
            await ctx.send("Member name has been updated")
        else:
            await ctx.send("Member does not exist")
        db.commit()

    #PRINT ROLES
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def printr(self, ctx):
        mycursor.execute("SELECT * FROM roles")
        result = mycursor.fetchall()
        for row in result:
            await ctx.send(str(row[0]) + " | " + str(row[1]) + " | " + str(row[2]))
        
    #PRINT MEMBERS
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def printm(self, ctx):
        mycursor.execute("SELECT name FROM members")
        result = mycursor.fetchall()
        for row in result:
            await ctx.send(str(row[0]))

def setup(bot):
    bot.add_cog(Database(bot))
    print("database check")
