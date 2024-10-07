import re
from functools import reduce
from model.Role import Role


def has_permission(discord_user, discord_message, session):

    if discord_user.id == discord_user.guild.owner_id:
        return True

    for discord_role in discord_user.roles:

        role_id = discord_role.id
        role = session.query(Role).filter(Role.discord_id == role_id).first()

        try:
            is_permitted = reduce(lambda s, perm: s or re.match(perm.regex, discord_message), role.permissions, False)
        except:
            continue

        if is_permitted:
            return True

    return False
