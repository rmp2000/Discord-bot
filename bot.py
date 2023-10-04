import os
import random

import aiohttp
import discord
import openai
import giphy_client

from discord.ext import commands
from discord.ui import Select,View
from discord import File

from easy_pil import load_image_async,Editor,Font
from giphy_client.rest import ApiException
from dotenv import load_dotenv

load_dotenv()

class MySelect(Select):
    async def callback(self,interaction):
            match self.values[0]:
                case "Lluvia":
                    respuesta="No se puede ir al gym, toca lol"
                case "Sol":
                    respuesta="Momento de salir a tocar la hierba"
                case "Nublado":
                    respuesta="Toca lol, no nos la podemos jugar a que llueva"
            await interaction.response.send_message(respuesta)

def run_discord_bot():
    TOKEN = os.getenv("discord_token")
    intents = discord.Intents.all()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.command(brief='repite lo que le dices', description='repite todas las palabras que dices despues del comando')
    async def di(ctx, *, arg):
        await ctx.send(arg)

    @bot.command(brief='Te da un saludito', description='Te da un saludito')
    async def saluda(ctx):
        await ctx.send(f"Hola {ctx.author} disftuta de tu estancia en PDG")

    @bot.command(brief='Lanza un gift de la palabra que quieras', description='Busca un gift de la palabra pasada como parametro, si no tiene ninguna usa happy como opcion')
    async def gift(ctx,*,q="happy"):
        api_key = os.getenv("gift_key")
        api_instance = giphy_client.DefaultApi()

        try:
            api_responce = api_instance.gifs_search_get(api_key,q,limit=6,rating="g")
            lis = list(api_responce.data)
            if lis:
                gif = random.choice(lis)
                embed=discord.Embed(title=q)
                embed.set_image(url=f"https://media.giphy.com/media/{gif.id}/giphy.gif")
                await ctx.send(embed=embed)
            else: 
                await ctx.send("Usa otra palabra esta no tiene gift sorry")

        except ApiException:
            print("Api exception")

    @bot.command(brief='Meme de anime cuidado puede tener algun spoiler', description='Pone un meme de anime que este en redit ese dia, puede tener spoiler es random no me hago responsable')
    async def animememe(ctx):
        async with aiohttp.ClientSession() as cd:
            async with cd.get("https://www.reddit.com/r/animememes.json") as r:
                animemes = await r.json()
                embed = discord.Embed(color=discord.Color.random())
                tamaño= len(animemes["data"]["children"])
                embed.set_image(url=animemes["data"]["children"][random.randint(0,tamaño-1)]["data"]["url"])
                
                await ctx.send(embed = embed )

    @bot.command(brief='Meme de lol ', description='Pone un meme de anime que este en redit ese dia')
    async def lolmeme(ctx):
        async with aiohttp.ClientSession() as cd:
            async with cd.get("https://www.reddit.com/r/LeagueOfMemes.json") as r:
                lolmeme = await r.json()
                embed = discord.Embed(color=discord.Color.random())
                tamaño = len(lolmeme["data"]["children"])
                embed.set_image(url=lolmeme["data"]["children"][random.randint(0,tamaño-1)]["data"]["url"])
                
                await ctx.send(embed = embed )

    @bot.command(brief='Dank meme ', description='Pone un meme que este en redit ese dia')
    async def dankmeme(ctx):
        async with aiohttp.ClientSession() as cd:
            async with cd.get("https://www.reddit.com/r/dankmemes.json") as r:
                dankmeme = await r.json()
                embed = discord.Embed(color=discord.Color.random())
                tamaño = len(dankmeme["data"]["children"])
                embed.set_image(url=dankmeme["data"]["children"][random.randint(0,tamaño-1)]["data"]["url"])
                
                await ctx.send(embed = embed )
      
    async def roll(ctx,valor:int=6):
        await ctx.send(random.randint(1,valor))

    @bot.command(brief='Hace el calculo que le pases despues de llamar a calcular', description='Haza el calculo, puede resolver operaciones complejas con diferentes simbolos matematicos')
    async def calcula(ctx,expresion):
        symbols=["+","-","*","/","%"]
        if any(s in expresion for s in symbols):
            calc = eval(expresion)
            embed = discord.Embed(title=":nerd: Actually :nerd:",description=f"Expresión : {expresion} \n Solución : {calc}",color=discord.Color.dark_gold())
        else:
            await ctx.send("Introduce una operación correcta")
        await ctx.send(embed=embed)

    @bot.command(brief='hace una encuesta: poner entre comillas todo, el primero sera la pregunta y las de despues las opciones', description='El primer argumento sera la pregunta los de despues las opciones hasta un maximo de 10 todo tiene que estar entre comillas ')
    async def encuesta(ctx, *args):
        if len(args)>11:
            await ctx.send("usa menos de 10 opciones")
            return
        embed=discord.Embed(title=args[0])
        tamaño=len(args)-1
        emo=["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        aux=""
        for i in range(1,tamaño+1):
            aux+=f"{emo[i-1]} {args[i]}\n"
        embed.add_field(name=f"{aux}",value="")
        mesasge_= await ctx.send(embed=embed)
        for i in range(0,tamaño):
            await mesasge_.add_reaction(emo[i])
    
    @bot.command(brief='No sabes que hacer, dile al bot que tiempo hace y lo descubriras', description="Selector de tiempo que da una respuesta dependiendo de la eleccion en el selector")
    async def tiempo(ctx):
        select=MySelect(
            placeholder="Que dia hace?",
            options=[
            discord.SelectOption(label="Lluvia ",emoji="🌧️",description="Llueve mucho"),
            discord.SelectOption(label="Sol",emoji="☀️",description="Soleado clima mediterraneo"),
            discord.SelectOption(label="Nublado",emoji="☁️",description="Un poco de nubes"),
        ])
        
        view=View()
        view.add_item(select)
        await ctx.send("Elige una opcion",view=view)

    @bot.command(brief="No va porque tienes que tenr la cuenta premium de chat gpt, estamos working en ello")
    async def gpt(ctx, *, arg):
        openai.api_key=os.getenv("openai_key")
        respuesta=openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=arg,
            temperature=0.7,
            max_tokens=10
            )
        final=respuesta.get("choice")
        if (not final):
           await ctx.send("Problemas con la api de chat gpt espera un poco")
        await ctx.send(final[0]["text"])

    @bot.command(brief='disponibles:ricardo,eugenio,kmpepo,javier,carlos,alejandro,minlok,roberto,xodos,iranzo,adrian', description="Pequeña frase en tono humoristico de los usuorios listados")
    async def persona(ctx, arg):
        dic= {
            "ricardo":"El mejor, el creador del bot",
            "eugenio":"Probablemente no pueda hablar porque esta chat restricted por no decir nada",
            "kmpepo":"Amigas gabriel esta en funcionamiento",
            "carlos":"No se encuentra en el servidor, busca en Torrent",
            "javier":"Esta trabajando, lo puedes encontrar jugando el IDLE mas malo de steam",
            "alejandro":"Haciendo split push",
            "minlok":"Desarrollando un videojuego que saldra en 2057 dejenle cocinar",
            "roberto":"una de pescado para la mesa 4",
            "xodos":"No se quien es esta persona desde que le pusieron la correa no se le volvio a ver",
            "iranzo":"Se busca, ultima vez visto aram nocturno 2021",
            "adrian":"Spoileando de anime seguramente"
            }
        persona=arg.lower()
        if persona in dic:
            await ctx.send(dic[persona])
        else:
            await ctx.send("Esta persona no se encuentra, comprueba que esta bien el nombre o ponte en contacto con el creador para añadirla")
        
    @bot.event
    async def on_ready():
        print(f'{bot.user} is now running')
    
    @bot.event
    async def on_member_join(member):
        channel = member.guild.system_channel

        backgrond=Editor("prueba.jpg")
        profile_image = await load_image_async(str(member.avatar.url))

        profile = Editor(profile_image).resize((150,150)).circle_image()
        poppins = Font.poppins(size=35,variant="bold")

        popings_small = Font.poppins(size=20,variant="light")

        backgrond.paste(profile,(325,50))
        backgrond.ellipse((325,50),150,150,outline="white",stroke_width=5)
        
        backgrond.text((400,260),f"BIENVENIDO A  {member.guild.name}",color="white",font=poppins,align="center")
        backgrond.text((400,300),f"{member.name}#{member.discriminator}",color="white",font=popings_small,align="center")

        file=File(fp=backgrond.image_bytes,filename="prueba.jpg")
        await channel.send(f"buenas {member.mention} bienvenido a {member.guild.name}")
        await channel.send(file=file)

    bot.run(TOKEN)
    