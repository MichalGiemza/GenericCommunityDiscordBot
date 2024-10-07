import datetime


class DateConverter:

    __supported_formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S']

    @classmethod
    def str_to_datetime(cls, time_string: str):

        for format in cls.__supported_formats:
            try:
                return datetime.datetime.strptime(time_string, format)
            except ValueError:
                pass

        raise ValueError('Unsupported format')
