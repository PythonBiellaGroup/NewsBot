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


def substack_list():
    """
    Richiama la lista newsletter in archivio per tutti
    i publisher nella lista SUBSTACK_LIST
    """
    dateResult, titleResult, llResult, textResult = [], [], [], []
    SUBSTACK_LIST = [
        ("https://stefanogatti.substack.com/archive/", "La Cultura del dato"),
        # ("https://aisupremacy.substack.com/archive/",
        #  "AI Supremacy"),
        ("https://www.bitecode.dev/archive/", "Bite code!"),
        ("https://alessandromolina.substack.com/archive/", "Python Data Engineering"),
    ]
    for f in SUBSTACK_LIST:
        alist, blist, clist, dlist = substack_scraper(
            defUrl=f[0],
            prefix_title=f[1],
        )
        dateResult = dateResult + alist
        titleResult = titleResult + blist
        llResult = llResult + clist
        textResult = textResult + dlist
    return dateResult, titleResult, llResult, textResult


def substack_scraper(defUrl, defNum=4, prefix_title=None):
    """
    Scraping della pagina di riepilogo delle newsletter
    in substack (presa da defUrl)

    "prefix_title" serve per dare un prefisso al titolo
    con la descrizione del substack
    """
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
    # Scraping del class precedente perchè quello sotto cambia sempre
    classList = bsObj.findAll(
        "div", {"class": "pencraft pc-display-flex pc-flexDirection-column pc-reset"}
    )
    # print(classList)
    linkList = []
    # La class precedente però viene assegnata anche alla data e scarto sempre i dispari
    for c in classList[0::2]:
        linkList.append(c.a)
    for link in linkList[0:defNum]:
        titolo = ""
        linkfinale = ""
        testo = ""
        try:
            linkfinale = link.get("href")
            # print(linkfinale,"\n\n")
            if not (linkfinale.startswith("http")):
                linkfinale = defUrl + linkfinale
            if prefix_title:
                titolo = f"{prefix_title} - {link.get_text().strip()}"
            else:
                titolo = link.get_text().strip()
            # print(titolo)
            # Occorre aprire link
            html2 = requests.get(linkfinale)
            # print(html2)
            bsOb2 = BeautifulSoup(html2.content, parser, from_encoding=encoding)
            tag_testo = bsOb2.find("div", {"class": "body markup"})
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
    alist, blist, clist, dlist = substack_list()
    for a, b, c, d in zip(alist, blist, clist, dlist):
        print(a)
        print(b)
        print(c)
        print(d)


if __name__ == "__main__":
    #test_scraper()
    pass
