import datetime
import json
import time
import traceback
import asyncio

import discord
from discord.ext import commands

import context
from config import reports_channel_id, announcements_channel_id, discord_token
from constants import command_prefix
from import_model import session
from message_management_system import MessageManagementSystem
from model.Command import Command
from model.User import User
from permission_tools import has_permission
from reaction_management_system import ReactionManagementSystem
from utils import *
from command_functions import CommandLoader, bot_commands
from utils import log
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
logger = setup_logger()
log(f'Starting Generic Community Discord Bot {datetime.datetime.now()}')
users_cache = dict()


if __name__ == '__main__':
    discord_client = discord.Client()

    async def handle_message(message, discord_user, is_edit):
        try:
            user = await get_user(message)

            # Awaited messages
            if await MessageManagementSystem.on_message(message, user):
                return

            # Command
            if message_to_reject(message):
                return

            arguments, command_name = await prepare_message_content(message)

            command = await get_command(command_name)

            if not command:
                return

            # Permissions
            if not has_permission(discord_user, message.content, session):
                raise PermissionError('You don\'t have permission to execute this command.')

            command_parameters = {'channel': message.channel, 'user': user, 'arguments': arguments, 'is_edit': is_edit,
                                  'bot': discord_client, 'discord_user': discord_user, 'message': message}

            return_message = await bot_commands[command.name](command_parameters)

            if return_message:
                await message.channel.send(return_message[:2000])

        except Exception as e:
            print(time.strftime("[!] Exception: %x %X"), flush=True)
            traceback.print_exc()
            try:
                await message.channel.send(f'**Unexpected error occurred:** ```{type(e).__name__}: {str(e)}```')
            except:
                log(f'Unexpected error occurred (no channel data): {type(e).__name__}: {str(e)}')

    @discord_client.event
    async def on_message(message):
        users_cache[message.author.id] = message.author
        await log_message(message, 'Message' if not message.author.bot else 'Bot message')
        await handle_message(message, message.author, is_edit=False)

    @discord_client.event
    async def on_message_edit(message_before, message):
        discord_user = users_cache[message.author.id]
        await log_message(message, 'Message edit' if not message.author.bot else 'Bot message edit')
        await handle_message(message, discord_user, is_edit=True)

    @discord_client.event
    async def on_message_delete(message):
        await log_message(message, 'Message delete')

    def message_to_reject(message):
        return not message.content.startswith(command_prefix) or (message.author.bot and not message.content.startswith(';refreshepisodes'))

    async def prepare_message_content(message):
        content = message.content.split()
        command_name = content[0][1:]
        arguments = content[1:]
        return arguments, command_name

    async def get_command(command_name):
        command = session.query(Command).filter(Command.name == command_name).first()
        return command

    async def get_user(message):
        user = session.query(User).filter(User.discord_id == message.author.id).first()
        if not user:
            # Register user
            new_user = User()
            new_user.discord_id = message.author.id
            new_user.name = str(message.author)
            session.add(new_user)
            session.commit()

            user = session.query(User).filter(User.discord_id == message.author.id).first()
        return user

    async def log_message(message, msg_type):
        log_content = {
            'text': str(message.content),
            'author': str(message.author),
            'channel': str(message.channel),
            'time': str(message.created_at)
        }
        log_msg = json.dumps(log_content)
        log(f'{msg_type}: ' + log_msg)

    async def log_user(user, msg_type):
        log_content = {
            'user': str(user),
            'time': str(datetime.datetime.now())
        }
        log_msg = json.dumps(log_content)
        log(f'{msg_type}: ' + log_msg)

    CommandLoader.load_commands()

    @discord_client.event
    async def on_reaction_add(reaction, user):
        log(f'Reaction from {user.name}: {reaction.emoji}')
        ReactionManagementSystem.reacted(reaction, reaction.message, user)

    @discord_client.event
    async def on_ready():
        # Status
        log('Generic Community Discord Bot getting ready...')
        activity = discord.Game(name='Command list ;help')
        await discord_client.change_presence(status=discord.Status.online, activity=activity)

        # Setting up context
        if not context.context_ready:
            context.bot = discord_client
            context.server = discord_client.guilds[0]
            context.reports_channel = discord.utils.get(context.server.channels, id=reports_channel_id)
            context.announcements_channel = discord.utils.get(context.server.channels, id=announcements_channel_id)

            context.context_ready = True
            log('Instances set.')

    bot = commands.Bot(command_prefix=command_prefix)
    discord_client.run(discord_token)
    discord_client.start()

