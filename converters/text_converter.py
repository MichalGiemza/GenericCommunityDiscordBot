import re

l_quote, r_quote = '„', '”'
pause_char = '—'


def eng_to_pl_quote_convert(eng_quote_sentence: str):
    sentence_left_fixed = re.sub('((?<=[\s|\}])|(?<=^))"', l_quote, eng_quote_sentence)
    sentence_fixed = re.sub('"((?<=\W)|(?<=$))', r_quote, sentence_left_fixed)

    return sentence_fixed


def minus_to_pause_converter(sentence: str):
    return re.sub('- ', f'{pause_char} ', sentence)
