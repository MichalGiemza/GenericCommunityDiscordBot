from model import *
from import_model import *
import os


if __name__ == '__main__':

    engine = create_engine(database_connection_string)

    Base.metadata.create_all(engine)
