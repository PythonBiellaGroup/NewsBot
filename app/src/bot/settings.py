#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import datetime
import pytz
import logging
import re
from itertools import islice
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# Set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
#logging.getLogger("settings").setLevel(logging.DEBUG)

LOGGER = logging.getLogger(__name__)

load_dotenv()
BOTNAME = os.environ.get('BOTNAME', None)
BOT_ID = os.environ.get('BOT_ID', None)
DEFAULT_FEED = os.environ.get('DEFAULT_FEED', None)

BOTTIMEZONE='Europe/Rome'
MESSAGE_SIZE_LIMIT=2000
# Limite al testo articoli in push
ARTICLE_TEXT_SIZE_LIMIT=500
burlescoDb=os.path.join('..', 'db', 'burlesco.db')

def adesso():
    st = datetime.datetime.now(pytz.timezone(BOTTIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')
    return st
    
#Data del giorno DD/MM/YYYY
def oggi():
    st = datetime.datetime.now(pytz.timezone(BOTTIMEZONE)).strftime('%d/%m/%y')
    return st

def full_escape_markdown(a_string):
    '''
    Elimina i caratteri speciali di Telegram
    Lista completa caratteri speciali telegram
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    '''  
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', a_string)


def escape_markdown(a_string):
    '''
    Elimina i caratteri speciali di Telegram
    Lista completa caratteri speciali telegram
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    '''  
    #Tolto *, usato nei messaggi per grassetto
    escape_chars = r'_[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', a_string)


def take(n, iterable):
    '''
    Return first n items of the iterable as a list
    '''
    return list(islice(iterable, n))