# -*- coding: utf-8 -*-
#!/usr/bin/python
import datetime
import pytz
import requests
import re
from bs4 import BeautifulSoup

BOTTIMEZONE = "Europe/Rome"


def adesso():
    st = datetime.datetime.now(pytz.timezone(BOTTIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    return st


def cleanText(text):
    if text:
        text = text.strip()
        text = re.sub(r"(\n)+", "\n", text, flags=re.UNICODE)
        text = re.sub(r"(\r)+", "\r", text, flags=re.UNICODE)
        text = re.sub(r"\n(\t)*(\s)*(\n)*", "\n", text, flags=re.UNICODE)
        text = re.sub(r"\r(\s)*\r", "\n", text, flags=re.UNICODE)
        text = re.sub(r"\r\n", "\n", text, flags=re.UNICODE)
    return text


def github_python_feed():
    dateResult, titleResult, llResult, textResult = [], [], [], []
    gh_feeds = [
        # Polars
        "https://github.com/pola-rs/polars/releases/latest",
        # FastAPI
        "https://github.com/tiangolo/fastapi/releases/latest",
        # Pydantic
        "https://github.com/pydantic/pydantic/releases/latest",
        # Functime
        "https://github.com/functime-org/functime/releases/latest",
        # PBG Website
        "https://github.com/PythonBiellaGroup/website/releases/latest",
        #UV
        "https://github.com/astral-sh/uv/releases/latest",
    ]
    for f in gh_feeds:
        alist, blist, clist, dlist = github_last_release(f)
        dateResult = dateResult + alist
        titleResult = titleResult + blist
        llResult = llResult + clist
        textResult = textResult + dlist
    return dateResult, titleResult, llResult, textResult


def github_last_release(defUrl):
    today = adesso()
    titleList = []
    llList = []
    textList = []
    dateList = []
    link = defUrl
    # Nome progetto dal link
    project = link.split("/")[4]
    try:
        html = requests.get(defUrl)
        encoding = (
            html.encoding
            if "charset" in html.headers.get("content-type", "").lower()
            else None
        )
        parser = "html.parser"  # or lxml or html5lib
    except requests.exceptions.HTTPError as errh:
        print("Http Error: ", errh)
        return dateList, titleList, llList, textList
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting: ", errc)
        return dateList, titleList, llList, textList
    except requests.exceptions.Timeout as errt:
        print("Timeout Error: ", errt)
        return dateList, titleList, llList, textList
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else: ", err)
        return dateList, titleList, llList, textList
    bsObj = BeautifulSoup(html.content, parser, from_encoding=encoding)
    tag_titolo = bsObj.find("h1", {"class": "d-inline mr-3"})
    titolo = f"Nuova release [{project}]: {tag_titolo.get_text()}"
    tag_testo = bsObj.find("div", {"class": "markdown-body my-3"})
    testo = tag_testo.get_text()
    if testo:
        testo = cleanText(testo)
        # print(testo)
    dateList.append(today)
    titleList.append(titolo)
    llList.append(link)
    textList.append(testo)
    return dateList, titleList, llList, textList


def test_scraper():
    alist, blist, clist, dlist = github_python_feed()
    for a, b, c, d in zip(alist, blist, clist, dlist):
        print(a)
        print(b)
        print(c)
        print(d)


if __name__ == "__main__":
    # test_scraper()
    pass
