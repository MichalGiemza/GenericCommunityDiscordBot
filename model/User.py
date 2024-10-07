from model import *


def _get_name(context):
    return context.get_current_parameters()['name']


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    discord_id = Column(String(discord_id_length), nullable=False)
    quiet_mode = Column(Boolean, nullable=False, default=False)
    name = Column(String(short_name_max_length), nullable=False)
    signature = Column(String(short_name_max_length), nullable=False, default=_get_name)
    warn_count = Column(Integer, nullable=False, default=0)

    # Methods
    @staticmethod
    def get_by_discord_id(session, discord_id):
        return session.query(User).filter(User.discord_id == discord_id).first()


init_table(User)
