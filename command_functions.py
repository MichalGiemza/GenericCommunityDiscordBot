import random
import traceback
import discord

from file_management_system import FileManagementSystem
from model.User import User
from model.Command import Command
from import_model import *
import context
import constants
from permission_tools import has_permission
from difflib import SequenceMatcher
from converters.database_data_converter import convert_value
from database_utility import *
import utils
from reaction_management_system import ReactionManagementSystem


commands = []
bot_commands = {}


class CommandLoader:

    @staticmethod
    def load_commands():
        try:
            session.query(Command).delete()
        except Exception as e:
            pass

        for command, command_name, command_help in commands:
            # Register Command
            new_command = Command()
            new_command.name = command_name
            new_command.help_text = command_help if command_help else '*No command description.*'
            session.add(new_command)
            session.flush()
            # Add command to dictionary
            bot_commands[command_name] = command

        session.commit()


async def hello_(parameters):
    return 'Hello, World!'
help_ = """Responds with Hello, World!"""
commands.append((hello_, 'hello', help_))


async def ask_for_input_dialog(channel, message_content, user, timeout=30):

    def check(m):
        return m.channel == channel and str(m.author.id) == user.discord_id

    await channel.send(message_content)
    msg = await context.bot.wait_for('message', check=check, timeout=timeout)

    return msg.content


async def db_(parameters):
    arguments = parameters['arguments']
    display_limit_warning = '*A maximum of 10 records are displayed.*'

    if not arguments:
        model_dir_content = os.listdir('model')
        model_files = filter(lambda x: '_' not in x, model_dir_content)
        tables = map(lambda mf: mf.replace('.py', ''), model_files)
        tables_text = reduce(lambda s, t: f'{s}, {t}', tables)

        return f'''**The `;db` command allows you to manipulate data in the database.**
`;db get table_name key=value` - allows you to preview selected records (e.g. name=UserName.1234), you can use multiple key-value pairs, or you can use none.
`;db set table_name id=record_id key=value` - allows you to modify a record with selected id, multiple key-value pairs can be used.
`;db add table_name key=value` - allows you to add a record, values from key-value pairs are entered into the record.
`;db del table_name key=value` - allows you to remove selected records (e.g. name=UserName.1234), you can use multiple key-value pairs, or you can use none.

**Tables in the database:**
*{tables_text}*
'''

    subcommand = arguments[0]
    table_name = arguments[1]

    table = get_table(table_name)

    if subcommand and 'get' == subcommand:

        fields, values = await get_multiple_conditions_from_arguments(arguments)
        objs = await filter_using_text_conditions(fields, table, values)

        display_dicts = list(map(lambda o: prepare_display_dict(o, hide_id=False), objs))
        display_results = map(lambda display_dict:
                              reduce(lambda s, c: f'{s}\n{c[0]}: {c[1]}', filter(lambda x: x[0] != "id", display_dict.items()),
                                     f'ID: {display_dict["id"]}'),
                              display_dicts)

        merged_result = reduce(lambda s, r: f'{s}```python\n{r}```', display_results, '')

        return f'Search results from table **{table_name}**:\n{merged_result} {display_limit_warning if len(display_dicts) >= 10 else ""}'[:2000]

    if subcommand and 'set' == subcommand:

        fields, values = await get_multiple_conditions_from_arguments(arguments)

        if not re.match('id', fields[0], re.IGNORECASE):
            raise ValueError("The first option must be: id=record_id.")

        obj = session.query(table).filter(table.id == values[0]).first()

        for field_name, value_str in zip(fields[1:], values[1:]):
            value = convert_value(field_name, value_str, table)
            setattr(obj, field_name, value)

        display_dict = prepare_display_dict(obj, hide_id=False)
        obj_str = reduce(lambda s, c: f'{s}\n{c[0]}: {c[1]}', filter(lambda x: x[0] != "id", display_dict.items()),
                                     f'ID: {display_dict["id"]}')

        session.commit()

        return f'Changes to record of table **{table_name}** have been saved.\n```python\n{obj_str}```'

    if subcommand and 'add' == subcommand:

        fields, values = await get_multiple_conditions_from_arguments(arguments)

        if 'id' in fields:
            raise ValueError("The id field is generated automatically.")

        obj = table()

        for field_name, value_str in zip(fields, values):
            value = convert_value(field_name, value_str, table)
            setattr(obj, field_name, value)

        session.add(obj)
        session.commit()
        obj = (await filter_using_text_conditions(fields, table, values)).first()

        display_dict = prepare_display_dict(obj, hide_id=False)
        obj_str = reduce(lambda s, c: f'{s}\n{c[0]}: {c[1]}', filter(lambda x: x[0] != "id", display_dict.items()),
                                     f'ID: {display_dict["id"]}')

        return f'Table object added **{table_name}**.\n```python\n{obj_str}```'

    if subcommand and 'del' == subcommand:

        fields, values = await get_multiple_conditions_from_arguments(arguments)
        objs = await filter_using_text_conditions(fields, table, values)

        display_dicts = list(map(lambda o: prepare_display_dict(o, hide_id=False), objs))
        display_results = map(lambda display_dict:
                              reduce(lambda s, c: f'{s}\n{c[0]}: {c[1]}', filter(lambda x: x[0] != "id", display_dict.items()),
                                     f'ID: {display_dict["id"]}'),
                              display_dicts)

        merged_result = reduce(lambda s, r: f'{s}```python\n{r}```', display_results, '')

        objs = await filter_using_text_conditions(fields, table, values, use_limit=False)
        objs.delete()
        session.commit()

        return f'The following items have been removed from the table **{table_name}**:\n{merged_result} {display_limit_warning if len(display_dicts) >= 10 else ""}'
help_ = """Allows database manipulation."""
commands.append((db_, 'db', help_))


async def filter_using_text_conditions(fields, table, values, use_limit=True):

    objs = session.query(table)

    for field_name, value_str in zip(fields, values):

        field = getattr(table, field_name)
        value = convert_value(field_name, value_str, table)

        objs = objs.filter(field == value)

    if use_limit:
        objs = objs.limit(10)

    return objs


async def get_multiple_conditions_from_arguments(arguments):
    try:
        x = reduce(lambda s, v: f'{s} {v}', arguments[2:]).strip()

        fields = list(map(lambda a: a.replace('=', ''), re.findall('[A-z_]+=', x)))
        values = re.split('\s*[A-z_]+=\s*', x)[1:]

    except Exception as e:
        fields = []
        values = []

    return fields, values


async def help_(parameters):
    user = parameters['arguments']
    discord_user = parameters['discord_user']

    msg = '### Available commands:'

    # Get all commands available
    commands = session.query(Command).all()
    allowed_commands = filter(lambda command: has_permission(discord_user, f';{command.name}', session), commands)

    msg += reduce(lambda s, command: f'{s} `;{command.name}` - {command.help_text}\n', allowed_commands, '\n')

    return msg
help_txt_ = """Displays available commands."""
commands.append((help_, 'help', help_txt_))


async def announce_(parameters):
    msg = parameters['message']
    channel = parameters['channel']
    user = parameters['user']
    text = msg.content[10:]
    img_url = msg.attachments[0].url if msg.attachments else None

    if not text:
        return 'To send an announcement, enter the command, add optional image and message text. `;announce content`'

    embed = discord.Embed(
        description=text,
        color=0x8a2ae3)

    if img_url:
        embed.set_image(url=img_url)

    # Select pinging method
    question_msg_text = '**Select publication method.**'
    question_msg_text += f'\n{constants.reaction_str_e} *Publish pinging everyone*'
    question_msg_text += f'\n{constants.reaction_str_h} *Publish pinging here*'
    question_msg_text += f'\n{constants.reaction_str_pen} *Publish without pinging*'
    question_msg_text += f'\n{constants.reaction_str_no} *Cancel*'
    available_reactions = [constants.reaction_str_e, constants.reaction_str_h, constants.reaction_str_pen,
                           constants.reaction_str_no]
    question_msg = await channel.send(question_msg_text)
    for ar in available_reactions:
        await question_msg.add_reaction(ar)
    result = await ReactionManagementSystem.wait_for_reactions(
        question_msg, available_reactions, users=[user], timeout=60)
    if result is None:
        raise TimeoutError('The time limit for a reaction response has expired.')
    else:
        reaction, _ = result
    if reaction.emoji == constants.reaction_str_no:
        return 'Publishing an announcement has been canceled.'

    message = await context.announcements_channel.send(embed=embed)

    if reaction.emoji == constants.reaction_str_e:
        await context.announcements_channel.send(f'@everyone')
    if reaction.emoji == constants.reaction_str_h:
        await context.announcements_channel.send(f'@here')
    if reaction.emoji == constants.reaction_str_pen:
        pass

    # Publish to other servers
    if message.channel.type == discord.ChannelType.news:
        await message.publish()

    return 'Announcement published.'
help_ = """Sends an announcement (with optional picture) to announcement channel. Ping choices are available."""
commands.append((announce_, 'announce', help_))


async def profile_(parameters):
    message = parameters['message']

    if message.mentions:
        # Specified user
        user = message.mentions[0]
    else:
        # User that sent message
        user = parameters['discord_user']

    msg = f'User profile: **{str(user.name)}**\n'
    msg += f' **Discord ID:** {user.id}\n'

    return msg
help_txt_ = """Displays user's profile."""
commands.append((profile_, 'profile', help_txt_))


async def report_(parameters):
    arguments = parameters['arguments']
    message = parameters['message']
    channel = parameters['channel']
    discord_user = parameters['discord_user']

    if len(arguments) == 1:
        # Create report
        reported_message, reported_message_channel = await get_message_and_channel_by_url(arguments[0], channel.guild.channels)

        msg = '**A report of a message containing inappropriate content was received.**\n'
        msg += f'**Channel:** {reported_message_channel.name}\n'
        msg += f'**Author:** {reported_message.author}\n'
        msg += f'**Reporting user:** {discord_user}\n'
        msg += f'**Link to the message:** {reported_message.jump_url}\n'
        if reported_message.content:
            msg += f'**Message content:** ```{reported_message.content.replace("`", "")[:1000]}```\n'
        if reported_message.attachments:
            msg += reduce(lambda s, u: f'{s}\n{u.url}', reported_message.attachments, '**Załączniki:**')[:500] + '\n'
        msg += '**Judgment?**'
        msg += f'\n{constants.reaction_str_bad} warning and deletion of message - paste the command below\n`;report punish {reported_message.jump_url}`'
        msg += f'\n{constants.reaction_str_good} cancel and remove the report - paste the command below\n `;report cancel {reported_message.jump_url}`'

        report_message = await context.reports_channel.send(msg)
        await message.add_reaction(constants.reaction_str_yes)

    elif len(arguments) == 2:
        # Take decision
        decision = arguments[0]
        reported_message, reported_message_channel = await get_message_and_channel_by_url(arguments[1], channel.guild.channels)

        if decision == 'punish':
            try:
                await reported_message.delete()
            except:
                return 'The reported message could not be deleted. It may have already been deleted manually.'
            await message.add_reaction(constants.reaction_str_yes)
        elif decision == 'cancel':
            await message.add_reaction(constants.reaction_str_yes)
        else:
            raise ValueError(f'Invalid argument: *{decision}*')

    else:
        # Information
        return 'To report a message for inappropriate content, right-click on it, select *Copy link with message, type the command, and paste the link.\n`;report link_with_message`'
help_txt_ = """Allows you to report messages containing inappropriate content."""
commands.append((report_, 'report', help_txt_))


async def get_message_and_channel_by_url(message_url, channels):
    _, _, _, _, _, reported_message_channel_id, reported_message_id = message_url.split('/')
    reported_message_channel = discord.utils.get(channels, id=int(reported_message_channel_id))
    reported_message = await reported_message_channel.fetch_message(int(reported_message_id))
    return reported_message, reported_message_channel

