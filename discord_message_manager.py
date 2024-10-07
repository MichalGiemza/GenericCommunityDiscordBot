from constants import *
import discord.utils
import asyncio


class DiscordMessageManager:

    @classmethod
    def send_message(cls, text, channel):

        msg = DiscordMessage(text, channel)
        msg.send()

        return msg


class DiscordMessage:

    event_loop = asyncio.get_event_loop()

    def __init__(self, text, channel):
        self.text = text
        self.channel = channel
        self.message = None

    def send(self):
        try:
            self.event_loop.run_until_complete(
                asyncio.wait([self.channel.send(self.text)]))
        except RuntimeError as e:
            pass

    def modify(self, new_text):
        try:
            self.event_loop.run_until_complete(
                asyncio.wait([self.message.edit(content=new_text)]))
        except RuntimeError as e:
            pass
