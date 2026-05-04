import logging
import os
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv
from ws_manager import PterodactylWS
from models import EventType

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
dev = os.getenv("DEVELOPER")
member_role = os.getenv("MEMBER_ROLE")
prefix = os.getenv("PREFIX")
mc_address = os.getenv("MC_ADDRESS")
mc_seed = f"{os.getenv('MC_SEED')}"

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=f"{prefix}", intents=intents)
ws_manager = PterodactylWS()

START_STOP_TIMEOUT = 120.0

# Start the ws_daemon
@bot.event
async def on_ready():
    bot.loop.create_task(ws_manager.run())
    print(f"We are ready to go in, {bot.user.name}")


# EVENTS:


@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")


# COMMANDS:
#
# Say Hello
@bot.command(help="Say hello")
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")


# ------------------------------------------------


# Dev command, only for developer
@bot.command(help="You shouldn't see this if you are not me")
@commands.has_role(dev)
async def dev_command(ctx):
    print(f"Dev command called, the author is {ctx.author.name}")
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
    if ws_manager.snapshot.status != "running":
        sent = await ws_manager.start()

        if sent:
            await ctx.send("Server is starting...")
            try:
                await asyncio.wait_for(ws_manager.waiters[EventType.SERVER_STARTED], timeout=START_STOP_TIMEOUT)
                await ctx.send("Server is now online ✅")
            except TimeoutError as e:
                print(f"Error: {EventType.SERVER_STARTED} Timeout Error")
                await ctx.send("Server start timed out")
            except asyncio.TimeoutError as e:
                print(f"Error: {EventType.SERVER_STARTED} Timeout Error")
                await ctx.send("Server start timed out")
            except asyncio.CancelledError as e:
                print(f"Error: {EventType.SERVER_STARTED} future was cancelled")
                await ctx.send("Server start was cancelled")
            except Exception as e:
                print(f"Error here {e}")
                await ctx.send("There was an error trying to start the server")
            finally:
                ws_manager.waiters.pop(EventType.SERVER_STARTED)
        else:
            await ctx.send("Server is already starting...")
    else:
        await ctx.send("Server is already online ✅")


@start.error
async def start_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Sorry, you need to be an mc member to start the server")


# ------------------------------------------------


# Stop the server
@bot.command(help="Stop the server (under development)")
@commands.has_role(member_role)
async def stop(ctx):
    if ws_manager.snapshot.status != "offline":
        sent = await ws_manager.stop()

        if sent:
            await ctx.send("Server is stopping...")
            try:
                await asyncio.wait_for(ws_manager.waiters[EventType.SERVER_STOPPED], timeout=START_STOP_TIMEOUT)
                await ctx.send("Server is now offline 🔴")
            except TimeoutError as e:
                print(f"Error: {EventType.SERVER_STOPPED} Timeout Error")
                await ctx.send("Server stop timed out")
            except asyncio.TimeoutError as e:
                print(f"Error: {EventType.SERVER_STOPPED} Timeout Error")
                await ctx.send("Server stop timed out")
            except asyncio.CancelledError as e:
                print(f"Error: {EventType.SERVER_STOPPED} future was cancelled")
                await ctx.send("Server stop was cancelled")
            except Exception as e:
                print(f"Error here: {e}")
                await ctx.send("There was an error trying to stop the server")
            finally:
                ws_manager.waiters.pop(EventType.SERVER_STOPPED)
        else:
            await ctx.send("Sorry! There's at least one player connected, or the server is already stopping")
    else:
        await ctx.send("Server is already offline 🔴")


@stop.error
async def stop_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Sorry, you need to be an mc member to stop the server")


# ------------------------------------------------


# Display server status
@bot.command(help="Display the server status (under development)")
@commands.has_role(member_role)
async def status(ctx):
    status = ws_manager.snapshot.status
    if status == "running":
        await ctx.send("The server is online ✅")
    elif status == "offline":
        await ctx.send("The server is offline 🔴")
    else:
        await ctx.send("Unknown Status")


@status.error
async def status_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Sorry, you need to be an mc member to use this command")


# ------------------------------------------------


# Display player count
@bot.command(help="Display player count of the server (under development)")
@commands.has_role(member_role)
async def players(ctx):
    await ctx.send(f"There are {ws_manager.snapshot.player_count} players online")


@players.error
async def players_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Sorry, you need to be an mc member to use this command")


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
            f"Role doesn't exist, please ask your sever admin to add the '{
                member_role
            }' role"
        )


# ------------------------------------------------


# Display the server address
@bot.command(help="Display server address")
async def address(ctx):
    if mc_address:
        await ctx.send(f"The server address is: {mc_address}", delete_after=30)
        await ctx.send("Guard it well.", delete_after=30)
    else:
        # await ctx.send("Sorry, I don't know the address ¯\_(ツ)_/¯")
        await ctx.send("Sorry, I don't know the address")


# ------------------------------------------------


# Display the server seed
@bot.command(help="Display the server seed")
async def seed(ctx):
    if mc_seed:
        await ctx.send(f"The server seed is: {mc_seed}.", delete_after=30)
    else:
        # await ctx.send("Sorry, I don't know the address ¯\_(ツ)_/¯")
        await ctx.send("Sorry, I don't know the address")


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
