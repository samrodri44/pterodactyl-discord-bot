import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from api import PterodactylWS

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
dev = os.getenv("DEVELOPER")
member_role = os.getenv("MEMBER_ROLE")
prefix = os.getenv("PREFIX")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=f"{prefix}", intents=intents)
ws_manager = PterodactylWS()


# Start the ws_daemon
@bot.event
async def on_ready():
    bot.loop.create_task(ws_manager.run())
    print(f"We are ready to go in, {bot.user.name}")


# EVENTS:


@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "shit" in message.content.lower():
        await message.channel.send(f"{message.author.mention} - don't use that word!")

    await bot.process_commands(message)


# COMMANDS:
#
# Say Hello
@bot.command(help="Say hello")
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")


# ------------------------------------------------


# Dev command, only for developer
@bot.command(help="You should'nt see this if you are not me")
@commands.has_role(dev)
async def dev_command(ctx):
    await ctx.send("Welcome back Mr. Stark")


@dev_command.error
async def dev_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Sorry, you do now have permission for this command")


# ------------------------------------------------


# Start the server
@bot.command(help="Start the server")
@commands.has_role(member_role)
async def start(ctx):
    # TODO: Implement
    await ws_manager.start()
    await ctx.send("Server is starting...")


@start.error
async def start_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Sorry, you need to be an mc member to start the server")


# ------------------------------------------------


# Stop the server
@bot.command(help="Stop the server")
@commands.has_role(member_role)
async def stop(ctx):
    # TODO:Implement
    await ctx.send("Server is stopping...")


@stop.error
async def stop_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Sorry, you need to be an mc member to stop the server")


# ------------------------------------------------


# Join as a member
@bot.command(help="Join as a member")
async def join(ctx):
    # TODO:Implement whitelist username addition
    role = discord.utils.get(ctx.guild.roles, name=member_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned to {member_role}")
    else:
        await ctx.send(
            "Role doesn't exist, please ask your sever admin to add the 'MC' role"
        )


# ------------------------------------------------


# Resign membership
@bot.command(help="Resign membership")
async def leave(ctx):
    # TODO:Implement whitelist username removal
    role = discord.utils.get(ctx.guild.roles, name=f"{member_role}")
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(
            f"{ctx.author.mention} has stopped being an {member_role} member"
        )
    else:
        await ctx.send("Role doesn't exist")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
