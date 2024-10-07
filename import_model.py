from model import *
from constants import *
from config import *
import importlib
import sys
import os
import sys
from functools import reduce
from sqlalchemy.orm import sessionmaker
import json


model_scripts_names = filter(lambda x: '_' not in x, os.listdir('model'))
model_module_names = map(lambda x: x[:-3], model_scripts_names)

this_module = sys.modules[__name__]
for module_name in model_module_names:
    module = importlib.import_module('model.%s' % module_name)
    setattr(this_module, module_name, getattr(module, module_name))

engine = create_engine(database_connection_string, connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

if __name__ == '__main__':
    print()
