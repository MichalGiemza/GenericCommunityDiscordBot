from converters.date_converter import DateConverter
from converters.boolean_converter import BooleanConverter


def convert_value(key, value, cls):

    key_type = str(getattr(cls, key).property.columns[0].type)

    if key_type == 'DATETIME':
        try:
            return DateConverter.str_to_datetime(value[:19])
        except:
            pass
    if key_type == 'BOOLEAN':
        try:
            return BooleanConverter.str_to_bool(value)
        except:
            pass

    # Couldn't convert
    if value == '':

        return None
    return value
