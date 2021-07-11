from discord.ext import commands
import discord
import os

client = commands.Bot(command_prefix = "g!")

Token = "ODU1MzU3MTYzNzUyNzgzODgz.YMxTbw.0VPKrU9Pdt-h2PGjjfE1MywBgcw"

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='This App Grows'))
    if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
        discord.opus.load_opus('opus')
    print("We have logged in as {}".format(client.user))

@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")

@client.command()
async def reload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

if __name__ == "__main__":
    client.run(Token)
