import sys
import requests
from bs4 import BeautifulSoup
import re
import feedparser
import ssl
import datetime
import pytz

# import settings
BOTTIMEZONE = "Europe/Rome"


def adesso():
    st = datetime.datetime.now(pytz.timezone(BOTTIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    return st


def feedStandard(
    defRSS,
    defNum=20,
    textTagFind="div",
    textTagAttribute="class",
    textTagAttributeValue="ls-articoloTesto",
    textFromRss=False,
    descriptionFromRssHTML=False,
    alternativeTextTagFind="div",
    alternativeTextTagAttribute="class",
    alternativeTextTagAttributeValue="post-content",
    prefix_title=None,
):
    """
    Generic function to feed from RSS url
    Returns tuple of lists: titoli, links, testi, date
    """
    if not defRSS:
        print("Manca parametro in input")
        raise AttributeError
    today = adesso()
    # Init outputs: titoli, links, testi, date
    titleList = []
    llList = []
    textList = []
    dateList = []
    # parse returns unicode strings, still strings
    if hasattr(ssl, "_create_unverified_context"):
        ssl._create_default_https_context = ssl._create_unverified_context
    d = feedparser.parse(defRSS)
    if d.bozo:
        print("XML not well formed. Bozo Exception", d.bozo_exception)
        titleList = []
        llList = []
        textList = []
        dateList = []
        return dateList, titleList, llList, textList
    for e in d.entries[0:defNum]:
        title = ""
        if prefix_title:
            title = f"{prefix_title} - {e.title.strip()}"
        else:
            title = e.title.strip()
        dateList.append(today)
        titleList.append(title)
        llList.append(e.link.strip())
        # Per i siti da dove non si riesce a prendere il testo dalla pagina-link
        if textFromRss:
            # Se description è a sua volta in HTML
            if descriptionFromRssHTML:
                bsObj = BeautifulSoup(e.description, "lxml")
                testo = bsObj.get_text()
                testo = re.sub(r"\s+", " ", testo, flags=re.UNICODE)
                textList.append(testo)
            else:
                # textList.append(e.description)
                textList.append(e.description)
            continue
        # Testo completo dell'articolo dal link
        try:
            html = requests.get(e.link).text.strip().encode("UTF-8")
            # html = requests.get(e.link)
            # encoding = requests.get(e.link).encoding if "charset" in requests.get(e.link).headers.get("content-type", "").lower() else None
            # bsOb2 = BeautifulSoup(html, "html.parser",from_encoding=encoding)
            bsOb2 = BeautifulSoup(html, "html.parser")
            # print(encoding)
            tag = bsOb2.find(textTagFind, {textTagAttribute: textTagAttributeValue})
            # Se find fallisce ritorna None
            if tag:
                try:
                    testo = tag.get_text()
                    # Elimina spazi in eccesso
                    testo = re.sub(r"\s+", " ", testo, flags=re.UNICODE)
                    textList.append(testo)
                except AttributeError:
                    # In caso di errore nel testo ripulisco gli ultimi valori
                    # print(ae)
                    dateList.pop()
                    titleList.pop()
                    llList.pop()
                    continue
                except Exception as e:
                    type, value, traceback = sys.exc_info()
                    print("feedStandard - Eccezione inaspettata: ")
                    print(type, value, traceback)
                    print(e)
                    dateList.pop()
                    titleList.pop()
                    llList.pop()
                    continue
            # Provo con alternative tags...
            else:
                tag = bsOb2.find(
                    alternativeTextTagFind,
                    {alternativeTextTagAttribute: alternativeTextTagAttributeValue},
                )
                try:
                    testo = tag.get_text()
                    # Elimina spazi in eccesso
                    testo = re.sub(r"\s+", " ", testo, flags=re.UNICODE)
                    textList.append(testo)
                except AttributeError as ae:
                    # In caso di errore nel testo ripulisco gli ultimi valori
                    print(ae)
                    dateList.pop()
                    titleList.pop()
                    llList.pop()
                    continue
                except Exception as e:
                    type, value, traceback = sys.exc_info()
                    print("feedStandard - Eccezione inaspettata: ")
                    print(type, value, traceback)
                    print(e)
                    dateList.pop()
                    titleList.pop()
                    llList.pop()
                    continue
        except requests.exceptions.SSLError as e:
            print("feedStandard - Errore nella request", e)
            titleList = []
            llList = []
            textList = []
            dateList = []
            return dateList, titleList, llList, textList
    return dateList, titleList, llList, textList


# MISSING UNIT TESTING
