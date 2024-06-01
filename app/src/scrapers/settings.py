#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import datetime
import pytz

BOTTIMEZONE = "Europe/Rome"
MESSAGE_SIZE_LIMIT = 2000
burlescoDb = os.path.join("..", "db", "burlesco.db")
# Env settings for Postgres db
PG_HOST = ""
PG_DBNAME = ""
PG_USER = ""
PG_PASSWORD = ""


def adesso():
    st = datetime.datetime.now(pytz.timezone(BOTTIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    return st


# Data del giorno DD/MM/YYYY
def oggi():
    st = datetime.datetime.now(pytz.timezone(BOTTIMEZONE)).strftime("%d/%m/%y")
    return st
