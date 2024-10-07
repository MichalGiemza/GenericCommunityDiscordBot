
class BooleanConverter:

    @classmethod
    def str_to_bool(cls, bool_string: str):

        bool_string = bool_string.title()
        if bool_string == 'True':
            return True
        if bool_string == 'False':
            return False

        raise ValueError('Unsupported format')
