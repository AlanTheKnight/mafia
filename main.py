import os
import configparser
import copy
import random
from typing import List, Dict, Union

import discord
from discord import utils
from discord.ext import commands

import manager


config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN: str = config["MAIN"]["TOKEN"]
GUILD: str = config["MAIN"]["GUILD"]
ADMINROLES: List[str] = config["MAIN"]["ADMINROLES"].split(" ")

intent: discord.Intents = discord.Intents.default()
intent.members = True
bot = commands.Bot(command_prefix="/", intents=intent)
users = manager.UserManager("users.json", bot)
roles = manager.RoleManager("roles.json", bot)


def is_admin(author: discord.Member) -> bool:
    rolenames = [i.name for i in author.roles]
    for i in ADMINROLES:
        if i in rolenames:
            return True
    return False


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print("Connected to the guild!")


@bot.command(name="join")
async def join(ctx: commands.Context):
    """Добавляет игрока"""
    if ctx.author.id in users:
        await ctx.send("Вы уже зарегистрированы.")
        return
    u = manager.User(ctx.author)
    users.addUser(u)
    users.save()
    await ctx.send("Вы зарегистрировались на игру.")


@bot.command(name="party")
async def party(ctx: commands.Context):
    """Выводит список игроков"""
    l = users.listUsers()
    if not l:
        await ctx.send("Игроков нет")
        return
    content = "Список игроков:\n" + "\n".join(
        [f"<@{user.id}>" for user in l]
    )
    await ctx.send(content)


@bot.command(name="remove")
@commands.has_role("ведущий")
async def remove(ctx: commands.Context):
    """Удаляет указанных игроков из игры"""
    m: discord.Message = ctx.message
    for user in m.mentions:
        users.removeUser(user.id)
    users.save()
    await ctx.send("Я успешно обновил список игроков")


@bot.command(name="clear")
@commands.has_role("ведущий")
async def clear(ctx: commands.Context):
    """Полностью очищает список игроков"""
    m: discord.Message = ctx.message
    users.data = {}
    users.save()
    await ctx.send("Я успешно очистил список игроков")


@bot.command(name="set-admin")
async def set_admin(ctx: commands.Context):
    """Задает ведущего"""
    if not is_admin(ctx.author):
        await ctx.send(f"Эту команду могут использовать только администраторы")
        return
    message: discord.Message = ctx.message
    role = utils.get(message.guild.roles, name="ведущий")
    member: discord.Member
    for member in role.members:
        await member.remove_roles(role)
    for member in message.mentions:
        await member.add_roles(role)
        break
    await ctx.send(f"Роль ведущего передана игроку <@{member.id}>")


class RolesCategory(commands.Cog, name="Роли"):
    @commands.command(name="add-role")
    @commands.has_role("ведущий")
    async def add_role(self, ctx: commands.Context, name: str):
        """Добавляет новую роль"""
        if name in roles:
            await ctx.send(f"Роль с именем \"{name}\" уже существует.")
            return
        roles.addRole(name)
        roles.save()
        await ctx.send(f"Роль \"{name}\" успешно добавлена!")

    @commands.command(name="add-image")
    @commands.has_role("ведущий")
    async def add_image(self, ctx: commands.Context, name: str):
        """Добавляет изображение к роли"""
        if name not in roles:
            await ctx.send("Роли с таким именем не существует")
        if not ctx.message.attachments:
            await ctx.send("Изображение не было прикреплено")
        image: discord.Attachment = ctx.message.attachments[0]
        extension: str = image.filename.split(".")[-1]
        if extension not in ["jpg", "png", "webp", "jpeg"]:
            await ctx.send("Неподдерживаемый формат файла")
        filename: str = "images/" + str(image.id) + "." + extension
        await image.save(filename)
        roles.data[name].image = filename
        await ctx.send("Изображение успешно добавлено!")
        roles.save()

    @commands.command(name="set")
    @commands.has_role("ведущий")
    async def set_amount(self, ctx: commands.Context, name: str, amount: str):
        """Задает количество игроков с указанной ролью"""
        if name not in roles:
            await ctx.send("Роли с таким именем не существует")
        roles.getRole(name).amount = int(amount)
        roles.save()
        await ctx.send("Количество успешно изменено")

    @commands.command(name="place")
    @commands.has_role("ведущий")
    async def set_channel(self, ctx: commands.Context, name: str):
        """Задает текстовый канал, где общаются игроки с указанной ролью"""
        if name not in roles:
            await ctx.send("Роли с таким именем не существует")
        channel_id: int = ctx.message.channel.id
        roles.getRole(name).channel_id = channel_id
        roles.save()
        await ctx.send(f"Канал роли изменен на <#{channel_id}>")

    @commands.command(name="roles")
    async def list_roles(self, ctx: commands.Context):
        """Выводит список ролей"""
        l = roles.listRoles()
        embed = discord.Embed(
            color=discord.Color.magenta()
        )
        for i in l:
            value = str(i.amount)
            if i.image is not None:
                value += " " + "\U0001f5bc"
            embed.add_field(name=i.name, value=value)
        await ctx.send(embed=embed)

    @commands.command(name="shuffle")
    @commands.has_role("ведущий")
    async def shuffle(self, ctx: commands.Context):
        """Перемешивает роли между участниками"""
        admin: discord.Member = ctx.message.author
        players = users.listUsers()
        roles_to_give = copy.deepcopy(roles.listGenRoles())
        if not players:
            await admin.send("Походу, раздавать роли некому")
            return
        if len(players) != roles.count:
            await admin.send("Количество ролей не совпадает с количеством игроков")
            return
        for player in players:
            to_give: manager.Role = random.choice(roles_to_give)
            if to_give.amount == 1:
                roles_to_give.remove(to_give)
            else:
                to_give.amount -= 1
            file = None
            if to_give.image:
                with open(to_give.image, "br") as f:
                    file = discord.File(f)
            member: discord.Member = ctx.guild.get_member(player.id)
            await member.send(
                f"Ты получил(а) роль \"{to_give.name}\"", file=file
            )
            if to_give.channel_id:
                channel: discord.TextChannel = ctx.guild.get_channel(to_give.channel_id)
                invite = await channel.create_invite(unique=False, max_age=300)
                await member.send(f"Вступи в текстовый канал своей роли: {invite}\nСсылка перестанет действовать через 300 секунд")
            await admin.send(f"Игрок {player.mention_name} получил роль {to_give.name}")
        await admin.send("Я раздал всем роли, играйте XD")

    @commands.command(name="rename")
    @commands.has_role("ведущий")
    async def rename(self, ctx: commands.Context, name1: str, name2: str):
        """Переименовывание роли"""
        if name1 not in roles:
            await ctx.send("Роли с таким именем не существует")
        roles.data[name1].name = name2
        roles.save()
        await ctx.send("Я успешно обновил название роли")

    @commands.command(name="delete")
    @commands.has_role("ведущий")
    async def delete(self, ctx: commands.Context, name: str):
        """Удаляет роль"""
        if name not in roles:
            await ctx.send("Роли с таким именем не существует")
        roles.deleteRole(name)
        roles.save()
        await ctx.send("Я успешно удалил роль")


bot.add_cog(RolesCategory())
bot.run(TOKEN)
