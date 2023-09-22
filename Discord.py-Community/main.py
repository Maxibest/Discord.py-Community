import discord
import os 
from discord.ext import commands
from dotenv import load_dotenv as supremacy
print (discord.__version__)
from json import load, dump 


bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"), intents = discord.Intents().all())

bot.remove_command("help")

supremacy(dotenv_path="config")

@bot.event
async def on_ready():
    print("bot prêt")

#création de ticket 
ticket_users = []

@bot.command(pass_context=True)
async def ticket(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title='Système de tickets',
        description='Cliquez sur 📩 pour créer un ticket.',
        color=0
    )
    embed.set_footer(text="Système de tickets")

    msg = await ctx.send(embed=embed)
    await msg.add_reaction("📩")

    def check(reaction, user):
        return str(reaction.emoji) == "📩" and reaction.message.id == msg.id and user != bot.user

    reaction, user = await bot.wait_for("reaction_add", check=check)

    if user.id not in ticket_users:
        ticket_users.append(user.id)

        # Création du canal textuel privé
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, read_message_history=True),
            guild.get_role(1073187594344792156): discord.PermissionOverwrite(read_messages=True) 
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{user.id}",
            overwrites=overwrites
        )

        await channel.send(f"Votre ticket a été créé ! {channel.mention} Si vous souhaitez fermer le ticket, utilisez la commande **?close**")

       # Supprimer la réaction de l'utilisateur
        await msg.remove_reaction("📩", user)

        # Supprimer le message du bot
        await msg.delete()

         # Supprimer la commande initiale de l'utilisateur
    await ctx.message.delete()
@bot.command(pass_context=True)
async def close(ctx):
    if ctx.channel.name.startswith("ticket-") and ctx.author.id in ticket_users:
        # Vérifie si la commande est exécutée dans un canal de ticket et si l'auteur est l'utilisateur du ticket

        # Supprimer le canal de ticket
        await ctx.channel.delete()
        ticket_users.remove(ctx.author.id)  # Retirer l'utilisateur de la liste des utilisateurs de tickets

    else:
        await ctx.send("Vous ne pouvez pas fermer ce ticket.")



#Permet de mettre une image après une commande
@bot.command(pass_context=True)
async def support(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('https://cdn.discordapp.com/attachments/1073667921403973642/Screenshot_002955_Picsart.png'.format(ctx)) 



@bot.command()
async def say(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(message)


#Ouvrir le fichier .json
@bot.command()
async def welcome(ctx, channel : discord.TextChannel):
    if channel in ctx.guild.channels:
        with open('Bienvenue.json', "r") as file:
            data = load(file)
        data[ctx.guild.id] = channel.id
        with open('Bienvenue.json', 'w') as file: 
            dump(data, file)
        await ctx.send(f"The channel {channel} is difined!")
    else : 
        await ctx.channel.send(f"The channel {channel } is does exist !")



#Envoie le Message welcome sous plusieurs serveurs avec le fichier .json
@bot.event
async def on_member_join(member) -> discord.Message:
    with open("Bienvenue.json", "r") as file:
        data = load(file)
    if str (member.guild.id) in data.keys():
        channel = bot.get_channel(data[str (member.guild.id)])
        await channel.send(f"Welcome !{member.mention}")



#Si la commande n'est pas exécutée sur le serveur spécifié, affichez 'erreur'.
@welcome.error
async def welcome_error(ctx, error):
    if isinstance(error, commands.ChannelNotFound):
        await ctx.send("Channel introuvable bg désolé !")

bot.run(os.getenv("TOKEN"))