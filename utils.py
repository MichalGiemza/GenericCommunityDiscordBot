import json
import logging
import datetime
import os
import sys
from functools import reduce
from urllib.parse import urlparse

import requests

import constants
from reaction_management_system import ReactionManagementSystem

weekday_map = {0: 'poniedziałek', 1: 'wtorek', 2: 'środa', 3: 'czwartek', 4: 'piątek', 5: 'sobota', 6: 'niedziela'}


def try_gv(function, default=None):
    try:
        return function()
    except Exception:
        return default


def log(message):
    logging.info(f'{datetime.datetime.now().strftime("%H:%M")} | {message}')


def setup_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(f'logs/{datetime.datetime.now().date()}.log', 'w+', 'utf-8')
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    logging.getLogger().setLevel(logging.INFO)

    return logger


def str_rel_date(day):
    day = day.date()
    today = datetime.datetime.now().date()
    timespan = day - today
    weekspan = day.isocalendar()[1] - today.isocalendar()[1]

    text_result = ''

    # dzisiaj/przeszły/przyszły
    if timespan.days == 0:
        return 'dzisiaj'

    if timespan.days > 0 and weekspan == 0:
        text_result += 'przyszły' if abs(day.weekday()) in [0, 1, 3, 4] else 'przyszła'

    if timespan.days < 0 and weekspan == 0:
        text_result += 'zeszły' if abs(day.weekday()) in [0, 1, 3, 4] else 'zeszła'

    # poniedziałek/wtorek/środa (...)
    text_result += f' {weekday_map[day.weekday()]}'

    # -/tydzień temu/za 2 tygodnie (...)
    if weekspan == 0:
        return text_result

    if weekspan > 0:
        week_count = abs(weekspan)
        if week_count == 1:
            week_text = determine_week_form(week_count)
        else:
            week_text = f'{week_count} {determine_week_form(week_count)}'

        text_result += f' za {week_text}'

    if weekspan < 0:
        week_count = abs(weekspan)
        if week_count == 1:
            week_text = determine_week_form(week_count)
        else:
            week_text = f'{week_count} {determine_week_form(week_count)}'

        text_result += f', {week_text} temu'

    return text_result.strip()


def determine_week_form(week_count):
    if week_count == 1:
        return 'tydzień'
    if 2 <=week_count <= 4:
        return 'tygodnie'
    if week_count >= 5:
        return 'tygodni'


def is_url(url: str):
    try:
        resp = urlparse(url)
        return resp.scheme and resp.netloc
    except:
        return False

