import random
import string
import constants
import requests
import os


class FileManagementSystem:

    @classmethod
    def download_file(cls, url, filename=None):

        filename = filename if filename is not None else cls.random_filename()

        stream = requests.get(url)

        with open(filename, 'wb') as f:
            f.write(stream.content)

        return filename

    @classmethod
    def remove_file(cls, filename):
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

    @classmethod
    def random_filename(cls):
        return ''.join([random.choice(string.ascii_letters) for i in range(16)])
