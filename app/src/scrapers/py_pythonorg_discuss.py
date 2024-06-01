#!/usr/bin/python
# -*- coding: utf-8 -*-
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


def python_discuss_scraper(
    defUrl="https://discuss.python.org/latest",
    baseUrl="https://discuss.python.org",
    defNum=10,
):
    today = adesso()
    # Init outputs
    titleList = []
    llList = []
    textList = []
    dateList = []
    try:
        html = requests.get(defUrl).text
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        return dateList, titleList, llList, textList
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        return dateList, titleList, llList, textList
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        return dateList, titleList, llList, textList
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
        return dateList, titleList, llList, textList
    bsObj = BeautifulSoup(html, "html.parser")
    # ora, titolo, link
    linkList = bsObj.findAll("span", {"class": "link-top-line"})
    for link in linkList[0:defNum]:
        titolo = ""
        linkfinale = ""
        testo = ""
        try:
            linkfinale = link.a.get("href")
            # print(linkfinale,"\n")
            if not (linkfinale.startswith("http")):
                linkfinale = defUrl + linkfinale
            titolo = link.a.get_text().strip()
            if not (titolo):
                continue
            # print(titolo,"\n")
            # Occorre aprire link
            html2 = requests.get(linkfinale).text
            # print(html2)
            # TODO: NON VA!
            bsOb2 = BeautifulSoup(html2, "html.parser")
            # print(bsOb2)
            tag_testo = bsOb2.find("div", {"class": "post"})
            if tag_testo:
                # print(tag_testo)
                testo = tag_testo.get_text()
                if testo:
                    testo = cleanText(testo)
            else:
                testo = titolo
            # print(testo)
        except AttributeError:
            continue
        except Exception as e:
            type, value, traceback = sys.exc_info()
            print("Eccezione inaspettata: ")
            print(type, value, traceback)
            print(e)
            print("\n")
        textList.append(testo)
        titleList.append(titolo)
        llList.append(linkfinale)
        dateList.append(today)
    return dateList, titleList, llList, textList


def test_scraper():
    alist, blist, clist, dlist = python_discuss_scraper()
    for a, b, c, d in zip(alist, blist, clist, dlist):
        print(a)
        print(b.encode("utf8"))
        print(c)
        print(d.encode("utf8"))


if __name__ == "__main__":
    # test_scraper()
    pass
