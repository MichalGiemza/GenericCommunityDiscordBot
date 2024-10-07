from model import *


class Command(Base):
    __tablename__ = 'command'
    id = Column(Integer, primary_key=True)
    name = Column(String(short_name_max_length), nullable=False)
    help_text = Column(String(help_text_length), nullable=True)


init_table(Command)
