#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import pytz
from newsFeedHelper import feedStandard

BOTTIMEZONE = "Europe/Rome"


def adesso():
    st = datetime.datetime.now(pytz.timezone(BOTTIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    return st


def youtube_python_feed():
    """
    Per trovar l'id, guardare sorgente home page del canale
    e cercare il valore di externalId
    """
    dateResult, titleResult, llResult, textResult = [], [], [], []
    yt_feeds = [
        (
            "https://www.youtube.com/feeds/videos.xml?channel_id=UCkvQcNjmC_duLhvDxeUPJAg",
            "Python Biella Group",
        ),
        (
            "https://www.youtube.com/feeds/videos.xml?channel_id=UCOyJ9ritUBmjXhoRXOFahJA",
            "Python Italia",
        ),
        (
            "https://www.youtube.com/feeds/videos.xml?channel_id=UCPlpwLjib1qOvtYp8_RtZ_A",
            "Python Milano",
        ),
        (
            "https://www.youtube.com/feeds/videos.xml?channel_id=UCVhQ2NnY5Rskt6UjCUkJ_DA",
            "Arjan codes",
        ),
        (
            "https://www.youtube.com/feeds/videos.xml?channel_id=UC0r6VVLgxKMpp-NGEEsE-MQ",
            "Politecnico di Milano",
        ),
        (
            "https://www.youtube.com/feeds/videos.xml?channel_id=UC2pTT29Xy8a7nwGgkFanCtA",
            "Claudio Cama",
        ),
        (
            "https://www.youtube.com/feeds/videos.xml?channel_id=UCG8b6j9mTYPxRG26gahFiDQ",
            "Xtream - AI Compass",
        ),
    ]
    for f in yt_feeds:
        alist, blist, clist, dlist = feedStandard(
            defRSS=f[0],
            textFromRss=True,
            descriptionFromRssHTML=True,
            prefix_title=f[1],
        )
        dateResult = dateResult + alist
        titleResult = titleResult + blist
        llResult = llResult + clist
        textResult = textResult + dlist
    return dateResult, titleResult, llResult, textResult


def test_scraper():
    alist, blist, clist, dlist = youtube_python_feed()
    for a, b, c, d in zip(alist, blist, clist, dlist):
        print(a)
        print(b)
        print(c)
        print(d)


if __name__ == "__main__":
    # test_scraper()
    pass
