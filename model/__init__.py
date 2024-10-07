from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Float, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
import datetime
from enum import Enum
import json
import re

Base = declarative_base()
discord_id_length = 20
discord_token_length = 60
prefix_max_chars = 4
short_name_max_length = 50
long_name_max_length = 250
help_text_length = 400
text_max_length = 2000
str_id_length = 36
notepad_txt_length = 1990


# Initialization
def init_table(cls):
    def str_(self):
        displayed_dict = dict(filter(lambda x: not re.search('(^_)', str(x[0])), self.__dict__.items()))
        return json.dumps(displayed_dict, sort_keys=True)

    cls.__str__ = str_


# Relationships 1 to n
def add_1_to_n_relation(cls, class_name: str, back_populate_name: str = "", field_name: str = ""):
    back_populate_name = back_populate_name if back_populate_name else cls.__name__.lower()
    field_name = class_name.lower() + 's' if not field_name else field_name

    setattr(cls, field_name, relationship(class_name, back_populates=back_populate_name,
                                          foreign_keys='%s.%s_id' % (class_name, back_populate_name)))


def add_n_to_1_relation(cls, class_name: str, back_populate_name: str = "", field_name: str = ""):
    foreign_table_name = class_name.lower()
    field_name = field_name if field_name else foreign_table_name
    back_populate_name = back_populate_name if back_populate_name else cls.__name__.lower() + 's'

    setattr(cls, '%s_id' % field_name, Column(Integer, ForeignKey('%s.id' % foreign_table_name), nullable=True))
    setattr(cls, field_name, relationship(class_name, back_populates=back_populate_name,
                                          foreign_keys=[getattr(cls, '%s_id' % field_name)]))


# Relationships 1 to 1
def add_1_to_1_relation_own_id(cls, class_name: str, back_populate_name: str = "", field_name: str = ""):
    back_populate_name = back_populate_name if back_populate_name else cls.__name__.lower()
    field_name = class_name.lower() if not field_name else field_name

    setattr(cls, field_name, relationship(class_name, back_populates=back_populate_name, uselist=False))


def add_1_to_1_relation_foreign_id(cls, class_name: str, back_populate_name: str = "", field_name: str = ""):
    foreign_table_name = class_name.lower()
    field_name = field_name if field_name else foreign_table_name
    back_populate_name = back_populate_name if back_populate_name else cls.__name__.lower()

    setattr(cls, '%s_id' % field_name, Column(Integer, ForeignKey('%s.id' % foreign_table_name), nullable=True))
    setattr(cls, field_name, relationship(class_name, back_populates=back_populate_name,
                                          foreign_keys=[getattr(cls, '%s_id' % field_name)]))


def add_1_to_1_unary_relation(cls, id_column, next_name: str = "", prev_name: str = ""):
    prev_id = Column(Integer, ForeignKey(f'{cls.__name__.lower()}.id'), nullable=True)
    setattr(cls, f'{prev_name}_id', prev_id)
    next_ = relationship(cls, backref=backref(prev_name, remote_side=[id_column]), uselist=False)
    setattr(cls, next_name, next_)
