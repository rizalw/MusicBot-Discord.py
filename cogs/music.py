from enum import auto
import discord
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands, tasks
from discord.ext.commands.core import command

import pafy
import nacl
import urllib
import re
import time

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = [] #isinya guild sama lagu yang lagi di queue (id/link)
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
        self.autoplay.start()
    
    @commands.command()
    async def ping(self, ctx):
        # await ctx.send(str(round(self.client.latency * 100)) + "ms")
        ping = str(round(self.client.latency * 100)) + " ms"
        embed=discord.Embed(color=0xffa200)
        embed.add_field(name="Ping " + str(ctx.author), value=ping, inline=False)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def clear(self, ctx, amount=100):
        channel = ctx.message.channel
        messages = []
        async for message in channel.history(limit=amount + 1):
            messages.append(message)
        await channel.delete_messages(messages)
        msg = await ctx.send('Messaged deleted.')
        time.sleep(5)
        await msg.delete()

    @commands.command(pass_context = True)
    async def join(self, ctx):
        if ctx.message.author.voice:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You're not in a voice channel")
    
    @commands.command(pass_context = True)
    async def leave(self, ctx):
        server = ctx.message.guild.voice_client
        await server.disconnect()

    @commands.command(pass_context = True)
    async def play(self, ctx, *url):

        channel = ctx.message.author.voice.channel
        voice = discord.utils.get(ctx.guild.voice_channels, name=channel.name)
        voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice_client == None:
            voice_client = await voice.connect()
        else:
            await voice_client.move_to(channel)
        #Check wheter the song is paused or not
        # print(voice_client.is_paused())
        if voice_client.is_paused() and len(url) == 0:
            voice_client.resume()
            return
        #Check whether the input is url or keyword
        html = self.check_link(url)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        
        #ketika queue kosong, jadi harus langsung di run
        if len(self.queue) == 0:
            await ctx.send("https://www.youtube.com/watch?v=" + video_ids[0])
            self.queue.append([ctx.message.guild, video_ids[0], int(ctx.message.channel.id)])
            song = pafy.new(video_ids[0])  # creates a new pafy object
            audio = song.getbest()  # gets an audio source
            source = FFmpegPCMAudio(audio.url, executable = "E:/Software/ffmpeg-2021-06-19-git-2cf95f2dd9-essentials_build/ffmpeg-2021-06-19-git-2cf95f2dd9-essentials_build/bin/ffmpeg.exe", **self.FFMPEG_OPTIONS)  # converts the youtube audio source into a source discord can use
            voice_client.play(source)  # play the source
        #ketika sudah ada isi  queue
        else:
            #Karena FIFO
            self.queue.append([ctx.message.guild, video_ids[0], int(ctx.message.channel.id)])

        # print("List of All Things")
        # for x in song.allstreams:
            # print(x)
        # for x in song.streams:
        #     print(x.rawbitrate)
        # print("\nList of audio Quality")
        # for x in song.audiostreams:
        #     print(x)

    @commands.command(pass_context = True)
    async def stop(self, ctx):
        voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice_client:
            if voice_client.is_playing():
                voice_client.stop()

    @commands.command(pass_context = True)
    async def pause(self, ctx):
        voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice_client:
            if voice_client.is_playing():
                voice_client.pause()
    
    @commands.command(pass_context = True)
    async def skip(self, ctx):
        voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        voice_client.stop()
        self.queue.pop(0)

    @commands.command(pass_Context = True)
    async def queue(self, ctx):
        print("Panjang queue:", len(self.queue))
        if len(self.queue) >= 1:
            await ctx.send("**Queue**")
            for x, y in enumerate(self.queue):
                myvid = pafy.new("https://www.youtube.com/watch?v=" + self.queue[x][1])
                await ctx.send(f"{x + 1}.  {myvid.title}")
        else:
            await ctx.send("Queue kosong")

    def check_link(self, data):
        if "v=" not in data[0]:
            keyword = "-".join(data)
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + keyword)
        else:
            search = data[0].split("v=")
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search[1])
        return html

    @tasks.loop(seconds = 5)
    async def autoplay(self):
        if len(self.queue) == 0:
            return
        print()
        for x in self.queue:
            print(x)
        voice_client = discord.utils.get(self.client.voice_clients, guild=self.queue[0][0])
        if not voice_client.is_playing():
            print(self.queue[0])
            html = self.check_link(self.queue[0][1])
            channel_id = self.queue[0][2]
            ctx = self.client.get_channel(channel_id)
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            await ctx.send("https://www.youtube.com/watch?v=" + video_ids[0])
            # self.queue.append([ctx.message.guild, video_ids[0]])
            song = pafy.new(video_ids[0])  # creates a new pafy object
            audio = song.getbest()  # gets an audio source
            source = FFmpegPCMAudio(audio.url, executable = "E:/Software/ffmpeg-2021-06-19-git-2cf95f2dd9-essentials_build/ffmpeg-2021-06-19-git-2cf95f2dd9-essentials_build/bin/ffmpeg.exe", **self.FFMPEG_OPTIONS)  # converts the youtube audio source into a source discord can use
            voice_client.play(source)  # play the source

    #For checking queue
    # async def background_task(self):
    #     while True:
    #         if len(self.queue) == 0:
    #             continue
    #         voice_client = discord.utils.get(self.client.voice_clients, guild=self.queue[0][0])
    #         if not voice_client.is_playing():
    #             await self.autoplay(voice_client)
    #             print("Berhasil 3")
    #         if len(self.queue) == 0:
    #             continue

def setup(client):
    client.add_cog(music(client))