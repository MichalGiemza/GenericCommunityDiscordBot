import asyncio
import logging

import context
from functools import reduce


class ReactionManagementSystem:

    waiting_functions = dict()

    @staticmethod
    async def wait_for_reactions(message, str_reactions=None, users=None, timeout=300, ignore_bot=True):

        def check(reaction, discord_user):

            user_ok = True
            if users is not None:
                user_ok = reduce(lambda s, u: s or str(discord_user.id) == u.discord_id, users, False)
            if ignore_bot and discord_user.bot is True:
                user_ok = False

            reaction_ok = True
            if str_reactions is not None:
                reaction_ok = str(reaction.emoji) in str_reactions

            return user_ok and reaction_ok and reaction.message.id == message.id

        try:
            reaction, user = await context.bot.wait_for('reaction_add', timeout=timeout, check=check)
        except asyncio.TimeoutError:
            logging.warning('Reaction timed out.')
            return None
        else:
            return reaction, user

    @classmethod
    def reacted(cls, reaction, reaction_message, user):

        success = False
        if reaction.emoji in cls.waiting_functions:
            functions = cls.waiting_functions[reaction.emoji]

            completed = []
            for function in functions:

                result = function(reaction_message=reaction_message, user=user)

                if result:
                    completed += result

                success |= result

            for function in completed:
                functions.remove(function)

        return success

    @classmethod
    def subscribe_reaction(cls, reaction_emoji, function):

        if reaction_emoji not in cls.waiting_functions:
            cls.waiting_functions[reaction_emoji] = []

        cls.waiting_functions[reaction_emoji].append(function)
