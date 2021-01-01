import json
import os
import discord
from typing import List, Dict, Union
from discord.ext import commands


class User:
    def __init__(self, user: discord.User = None, data=None):
        if data is not None:
            self.name = data["name"]
            self.id = data["id"]
            return
        self.name = user.name
        self.id = user.id

    @property
    def mention_name(self):
        return f"<@{self.id}>"

    def save(self):
        return {
            "name": self.name,
            "id": self.id
        }


class UserManager:
    def __init__(self, filename: str, bot: commands.Bot):
        self.filename = filename
        self.data: Dict[int, User] = {}
        self.bot = bot

        if os.path.isfile(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                self.data = {int(i): User(data=data[i]) for i in data}

    def save(self):
        data = {i.id: i.save() for i in self.data.values()}
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def removeUser(self, user_id: int):
        if user_id in self.data:
            del self.data[user_id]
    
    def addUser(self, user: User):
        self.data[user.id] = user

    def listUsers(self) -> List[User]:
        return list(self.data.values())

    def __contains__(self, value):
        return value in self.data


class Role:
    __attrs = ["name", "image", "channel_id", "amount"]

    def __init__(self, name: str, image: Union[None, str] = None,
                 channel_id: Union[None, int] = None, amount: int = 0):
        self.name = name
        self.image = image
        self.channel_id = channel_id
        self.amount = amount
    
    def save(self):
        return {i: getattr(self, i) for i in self.__attrs}


class RoleManager:
    def __init__(self, filename: str, bot: commands.Bot):
        self.filename = filename
        self.data: Dict[str, Role] = {}
        self.bot = bot

        if os.path.isfile(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                self.data = {i: Role(**data[i]) for i in data}

    def __contains__(self, value):
        return value in self.data
    
    def addRole(self, role_name: str):
        self.data[role_name] = Role(role_name)
    
    def listRoles(self) -> List[Role]:
        return list(self.data.values())
    
    def deleteRole(self, role_name) -> None:
        if role_name in self.data:
            del self.data[role_name]
    
    def listGenRoles(self) -> List[Role]:
        return [i for i in self.data.values() if i.amount > 0]
    
    def getRole(self, role_name) -> Role:
        return self.data[role_name]
    
    def save(self):
        data = {i.name: i.save() for i in self.data.values()}
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @property
    def count(self):
        count = 0
        for i in self.listRoles():
            count += i.amount
        return count
