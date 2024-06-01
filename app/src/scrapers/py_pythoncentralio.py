#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import pytz
from newsFeedHelper import feedStandard

BOTTIMEZONE = "Europe/Rome"


def adesso():
    st = datetime.datetime.now(pytz.timezone(BOTTIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    return st


def python_central_scraper():
    return feedStandard(
        defRSS="https://www.pythoncentral.io/feed/",
        textFromRss=True,
        descriptionFromRssHTML=True,
    )


def test_scraper():
    alist, blist, clist, dlist = python_central_scraper()
    for a, b, c, d in zip(alist, blist, clist, dlist):
        print(a)
        print(b.encode("utf8"))
        print(c)
        print(d.encode("utf8"))


if __name__ == "__main__":
    # test_scraper()
    pass
