import re


def get_table(table_name):
    imports = __import__('__main__')
    table = getattr(imports, table_name)
    return table


def prepare_display_dict(obj, hide_id=True):
    pattern_relationships = '.relationships.RelationshipProperty.'
    pattern = '(^_)|(^id$)' if hide_id else '(^_)'

    items = obj.__dict__.items()
    items = filter(lambda x: not (hasattr(x[1], 'comparator') and pattern_relationships in str(x[1].comparator)), items)
    items = filter(lambda x: not re.search(pattern, str(x[0])), items)

    return dict(items)
