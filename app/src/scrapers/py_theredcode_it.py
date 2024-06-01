#!/usr/bin/python
import datetime
import sys
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


def theredcode_scraper(defUrl="https://www.theredcode.it/posts/", defNum=10):
    # sys.setdefaultencoding("utf-8")
    today = adesso()
    # Init outputs
    titleList = []
    llList = []
    textList = []
    dateList = []
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
    linkList = bsObj.findAll("div", {"class": "blog-post-title"})
    for link in linkList[0:defNum]:
        titolo = ""
        linkfinale = ""
        testo = ""
        try:
            linkfinale = link.a.get("href")
            # print(linkfinale,"\n")
            if not (linkfinale.startswith("http")):
                linkfinale = defUrl + linkfinale
            titolo = link.get_text().strip()
            # print(titolo)
            # Occorre aprire link
            html2 = requests.get(linkfinale)
            # print(html2)
            bsOb2 = BeautifulSoup(html2.content, parser, from_encoding=encoding)
            tag_testo = bsOb2.find("div", {"class": "single-blog-content"})
            testo = tag_testo.get_text()
            if testo:
                testo = cleanText(testo)
                # print(testo)
            if not (titolo):
                # Salto
                continue
        except AttributeError:
            # Salto
            continue
        except Exception as e:
            type, value, traceback = sys.exc_info()
            print("Eccezione inaspettata: ")
            print(type, value, traceback)
            print(e)
            print("\n")
            pass
        dateList.append(today)
        titleList.append(titolo)
        llList.append(linkfinale)
        textList.append(testo)
    return dateList, titleList, llList, textList


def test_scraper():
    alist, blist, clist, dlist = theredcode_scraper()
    for a, b, c, d in zip(alist, blist, clist, dlist):
        print(a)
        print(b)
        print(c)
        print(d)


if __name__ == "__main__":
    # test_scraper()
    pass
