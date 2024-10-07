from model import *


class Permission(Base):
    __tablename__ = 'permission'
    id = Column(Integer, primary_key=True)
    regex = Column(String(short_name_max_length), nullable=False)


add_n_to_1_relation(Permission, 'Role')
init_table(Permission)
