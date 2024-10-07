from model import *


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String(short_name_max_length), nullable=False)
    discord_id = Column(String(discord_id_length), nullable=False)


add_1_to_n_relation(Role, 'Permission')
init_table(Role)
