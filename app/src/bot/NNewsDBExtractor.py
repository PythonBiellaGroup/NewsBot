import sqlite3
import sys
import re
import settings

logger = settings.LOGGER


# Funzione necessaria per cercare in SQL con REGEXP per gli "interessi" da tutti gli articoli
# Aggiunta opzione ignore case
def regexp(expr, item):
    reg = re.compile(expr, re.IGNORECASE)
    return reg.search(item) is not None


def feedList(catList):
    """
    CATEGORY
    Ritorna la lista id FEEDs come stringa pronta per la query
    """
    logger.debug(f"Funzione feedList: input {catList}")
    conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
    c = conn.cursor()
    feeds = ""
    try:
        query = f"SELECT a.idSorgente FROM sorgente a, categoria b where b.idCategoria = a.idCategoria and b.idCategoria in ({catList})"
        logger.debug(query)
        c.execute(query)
        exists = c.fetchall()
        if exists:
            # Costruisce la lista/stringa
            feeds = ",".join((str(n[0]) for n in exists))
        else:
            raise ValueError(f"Nessun feed per le categorie in: {catList}")
    except Exception as e:
        logger.error("Eccezione durante la SELECT", sys.exc_info()[0])
        logger.error(e)
        pass
    conn.close()
    logger.debug(f"Funzione feedList: output {feeds}")
    return feeds


def catUtentiExtractor():
    """
    CATEGORY
    Estrae lista utenti che hanno almento un categoria con relativo categoria (come id) e massimo articolo id già spedito raggiunto
    """
    # Lista regular expression da ricercare
    catList = []
    idUserList = []
    maxList = []
    conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
    c = conn.cursor()

    try:
        # for row in c.execute("select idUser, catLastArticolo, catList from interessi where catList <> '' or catList <> '0' or catList is not null"):
        for row in c.execute(
            "select a.idUser, a.catLastArticolo, a.catList from interessi a, utenti b where a.idUser = b.idUser and b.banned=0 and (a.catList <> '' or a.catList <> '0' or a.catList is not null)"
        ):
            idUserList.append(row[0])
            maxList.append(row[1])
            catList.append(row[2])
            logger.debug(f"Record: {row}")
    except Exception as e:
        logger.error(
            "(sorgentiUtentiExtractor) eccezione durante la select", sys.exc_info()[0]
        )
        logger.error(e)
        pass
    conn.close()
    logger.debug(f"Output catUtentiExtractor {idUserList}, {catList}, {maxList}")
    return idUserList, catList, maxList


def articoliPerCat(catList, fromArtId):
    """
    Input:
    - catList: lista categorie da considerare nell'estrazione
    - fromArtId: articolo id da cui partire nell'estrazione
    Output:
    - lista messaggi da inviare
    - nuovo maxId
    """
    logger.debug(f"Funzione articoliPerCat, input {catList}; {fromArtId}")
    idArtList = []
    titleList = []
    linkList = []
    sorgenteList = []
    data_art_list = []
    fonte_list = []
    testo_list = []
    MAX_ID = 0
    conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
    c = conn.cursor()
    # Estraggo la lista sorgenti sorgenteList delle categorie in catList
    sorgenteList = feedList(catList)
    logger.debug(f"Lista sorgenti {sorgenteList}")
    # Estraggo gli articoli di interesse
    sqlString = f"""
    SELECT a.idArticolo, a.titolo, a.link, a.data, s.sorgente, a.testo
    FROM articoli a, categoria c, sorgente s 
    where s.idCategoria = c.idCategoria 
    and s.idSorgente = a.idSorgente
    and a.idSorgente in ({sorgenteList})
    and a.idArticolo > ? 
    order by a.idArticolo asc
    """
    logger.debug(f"sqlString {sqlString}")
    try:
        for row1 in c.execute(sqlString, (fromArtId,)):
            idArtList.append(int(row1[0]))
            titleList.append(row1[1])
            linkList.append(row1[2])
            data_art_list.append(row1[3])
            fonte_list.append(row1[4])
            testo_list.append(row1[5])
    except Exception as e:
        logger.error("(articoliPerCat) Eccezione durante la select", sys.exc_info()[0])
        logger.error(f"Sorgente / id: {sorgenteList}, {fromArtId}")
        logger.error(e)
    conn.close()
    # Costruzione output
    msg_list = []
    # Se ci sono articoli
    if len(idArtList) > 0:
        logger.debug(f"Ci sono {len(idArtList)} articoli...")
        # Max art id è l'ultimo...
        MAX_ID = row1[0]
        messaggio = ""
        for title, link, data, fonte, testo in zip(
            titleList, linkList, data_art_list, fonte_list, testo_list
        ):
            logger.debug(title)
            if len(testo) > settings.ARTICLE_TEXT_SIZE_LIMIT:
                testo = testo[0 : settings.ARTICLE_TEXT_SIZE_LIMIT] + "..."
            messaggio = f"[{data}] da ({fonte})\n{title}\n\n"
            messaggio = messaggio + testo
            messaggio = messaggio + "\n" + link
            msg_list.append(messaggio)
    else:
        logger.debug("Non ci sono articoli estratti per categoria...")
    logger.debug(f"articoliPerCat restituisce {MAX_ID} e {msg_list}")
    return MAX_ID, msg_list


def sorgentiUtentiExtractor():
    """
    SORGENTI
    Estrae lista utenti che hanno almento un interesse
    con relativo interesse (come id)
    e massimo articolo raggiunto (come id) già spedito
    """
    # Lista regular expression da ricercare
    logger.debug("(sorgentiUtentiExtractor) inizio...")
    sorgenteList = []
    idUserList = []
    maxList = []
    conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
    c = conn.cursor()
    try:
        # for row in c.execute("select idUser, sourceLastArticolo, sourceList from interessi where sourceList <> '' or sourceList <> '0' or sourceList is not null"):
        for row in c.execute(
            "select a.idUser, a.sourceLastArticolo, a.sourceList from interessi a, utenti b where a.idUser = b.idUser and b.banned=0 and (a.sourceList <> '' or a.sourceList <> '0' or a.sourceList is not null)"
        ):
            idUserList.append(row[0])
            maxList.append(row[1])
            sorgenteList.append(row[2])
            logger.debug(f"sorgentiUtentiExtractor row: {row}")
    except Exception as e:
        logger.error(
            f"(sorgentiUtentiExtractor) eccezione durante la select: {sys.exc_info()[0]}"
        )
        logger.error(e)
        pass
    conn.close()
    logger.debug(
        f"(sorgentiUtentiExtractor) restituisce: {idUserList}, {sorgenteList}, {maxList}"
    )
    return idUserList, sorgenteList, maxList


def interessiUtentiExtractor():
    """
    TOPIC
    OUTPUT
    List idUtenti, topics (come RE), max articolo id già spedito raggiunto
    """
    # Lista regular expression da ricercare
    logger.debug("(interessiUtentiExtractor) inizio...")
    topicList = []
    idUserList = []
    maxList = []
    conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
    c = conn.cursor()
    try:
        # for row in c.execute("select idUser, lastArticolo, topicList from interessi where topicList <> '' or topicList <> '0' or topicList is not null"):
        for row in c.execute(
            "select a.idUser, a.lastArticolo, a.topicList from interessi a, utenti b where a.idUser = b.idUser and b.banned=0 and (a.topicList <> '' or a.topicList <> '0' or a.topicList is not null)"
        ):
            idUserList.append(row[0])
            maxList.append(row[1])
            topicList.append(row[2])
            # print(row)
    except Exception as e:
        logger.error(
            f"(interessiUtentiExtractor) Eccezione durante la select: {sys.exc_info()[0]}"
        )
        logger.error(e)
    conn.close()
    logger.debug(
        f"(interessiUtentiExtractor) restituisce: {idUserList}, {topicList}, {maxList}"
    )
    return idUserList, topicList, maxList


def articoliPerTopic(topic, fromArtId):
    """
    ESTRAZIONE ARTICOLI PER TOPIC (parole chiavi)
    INPUT
    - topic (string): regular expression da cercare negli articoli
    - fromArtId (int): articolo da cui partire
    OUTPUT
    - nuovoArtId (int): nuovo max articolo
    - lista articoli (list of strings) - messaggi dal bot
    """
    logger.debug(f"articoliPerTopic inizio: param {topic} e {fromArtId}")
    idArtList = []
    titleList = []
    linkList = []
    data_art_list = []
    fonte_list = []
    testo_list = []
    MAX_ID = 0
    conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
    # interessi sono in formato REGEXP
    conn.create_function("REGEXP", 2, regexp)
    d = conn.cursor()
    # Estraggo gli articoli di interesse
    sqlString = """
    SELECT a.idArticolo, a.titolo, a.link, a.data, s.sorgente, a.testo
    FROM articoli a, categoria c, sorgente s 
    where s.idCategoria = c.idCategoria 
    and s.idSorgente = a.idSorgente
    and a.titolo REGEXP ? COLLATE NOCASE 
    and a.idArticolo > ? 
    order by a.idArticolo asc
    """
    logger.debug(f"sqlString {sqlString}")
    try:
        for row1 in d.execute(sqlString, (topic, fromArtId)):
            idArtList.append(int(row1[0]))
            titleList.append(row1[1])
            linkList.append(row1[2])
            data_art_list.append(row1[3])
            fonte_list.append(row1[4])
            testo_list.append(row1[5])
    except Exception as e:
        logger.error(
            f"(articoliPerTopic) Eccezione durante la select: {sys.exc_info()[0]}"
        )
        logger.error(e)
        pass
    conn.close()
    msg_list = []
    # Se ci sono articoli
    if len(idArtList) > 0:
        logger.debug(f"Ci sono {len(idArtList)} articoli...")
        MAX_ID = row1[0]
        messaggio = ""
        for title, link, data, fonte, testo in zip(
            titleList, linkList, data_art_list, fonte_list, testo_list
        ):
            logger.debug(title)
            if len(testo) > settings.ARTICLE_TEXT_SIZE_LIMIT:
                testo = testo[0 : settings.ARTICLE_TEXT_SIZE_LIMIT] + "..."
            messaggio = f"[{data}] da ({fonte})\n{title}\n\n"
            messaggio = messaggio + testo
            messaggio = messaggio + "\n" + link
            msg_list.append(messaggio)
    else:
        logger.debug("Non ci sono articoli estratti per topic...")
    logger.debug(f"articoliPerTopic restituisce {MAX_ID} e {msg_list}")
    return MAX_ID, msg_list


def articoliPerSorgente(lista_sorgenti, fromArtId):
    """
    ESTRAZIONE ARTICOLI PER SORGENTI
    INPUT
    - lista_sorgenti: lista id sorgenti
    - fromArtId (int) - articolo da cui partire
    OUTPUT
    - nuovoArtId (int)
    - lista articoli (list of strings)
    """
    logger.debug(
        f"Estrazione articoli per SORGENTI inizio: param {lista_sorgenti} e {fromArtId}"
    )
    idArtList = []
    titleList = []
    linkList = []
    data_art_list = []
    fonte_list = []
    testo_list = []
    MAX_ID = 0
    conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
    c = conn.cursor()
    sqlString = f"""
    SELECT a.idArticolo, a.titolo, a.link, a.data, s.sorgente, a.testo
    FROM articoli a, categoria c, sorgente s 
    where s.idCategoria = c.idCategoria 
    and s.idSorgente = a.idSorgente
    and a.idSorgente in ({lista_sorgenti})
    and a.idArticolo > ? 
    order by a.idArticolo asc
    """
    logger.debug(f"sqlString {sqlString}")
    try:
        for row1 in c.execute(sqlString, (fromArtId,)):
            idArtList.append(int(row1[0]))
            titleList.append(row1[1])
            linkList.append(row1[2])
            data_art_list.append(row1[3])
            fonte_list.append(row1[4])
            testo_list.append(row1[5])
    except Exception as e:
        logger.error(
            f"(articoli per sorgente) Eccezione durante la select: {sys.exc_info()[0]}"
        )
        logger.error(f"Sql: {sqlString}")
        logger.error(f"Sorgente {lista_sorgenti}/ id: {fromArtId}")
        logger.error(e)
    conn.close()
    msg_list = []
    # Se ci sono articoli
    if len(idArtList) > 0:
        logger.debug(f"Ci sono {len(idArtList)} articoli...")
        MAX_ID = row1[0]
        messaggio = ""
        for title, link, data, fonte, testo in zip(
            titleList, linkList, data_art_list, fonte_list, testo_list
        ):
            logger.debug(title)
            if len(testo) > settings.ARTICLE_TEXT_SIZE_LIMIT:
                testo = testo[0 : settings.ARTICLE_TEXT_SIZE_LIMIT] + "..."
            messaggio = f"[{data}] da ({fonte})\n{title}\n\n"
            messaggio = messaggio + testo
            messaggio = messaggio + "\n" + link
            msg_list.append(messaggio)
    else:
        logger.debug("Non ci sono articoli estratti per sorgente...")
    logger.debug(f"articoliPerSorgente restituisce {MAX_ID} e {msg_list}")
    return MAX_ID, msg_list


def updateMaxArt(idUser, newMax):
    """
    TOPIC
    Funzione per update ultimo articolo letto
    """
    logger.debug(f"updateMaxArt inizio: param {idUser} e {newMax}")
    conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
    c = conn.cursor()
    try:
        c.execute(
            "update interessi set lastArticolo = ? where idUser = ?",
            (newMax, int(idUser)),
        )
    except sqlite3.OperationalError as e:
        logger.error(
            "(updateMaxArt) Sqlite operational error: {}, newMax: {}, idUser: {} Retrying...".format(
                e, newMax, int(idUser)
            )
        )
    except Exception as e:
        logger.error(
            f"(updateMaxArt) Eccezione durante la update di lastArticolo per l'utente {str(idUser)}; {sys.exc_info()[0]}"
        )
        logger.error(e)
    conn.commit()
    conn.close()
    return


def updateMaxSourceArt(idUser, newMax):
    """
    SORGENTI
    Funzione per update ultimo articolo letto
    """
    conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
    c = conn.cursor()
    try:
        c.execute(
            "update interessi set sourceLastArticolo = ? where idUser = ?",
            (newMax, int(idUser)),
        )
    except sqlite3.OperationalError as e:
        logger.error(
            "(updateMaxSourceArt) Sqlite operational error: {}, newMax: {}, idUser: {} Retrying...".format(
                e, newMax, int(idUser)
            )
        )
    except Exception as e:
        logger.error(
            "(updateMaxSourceArt) Eccezione durante la update di sourceLastArticolo per l'utente "
            + str(idUser),
            sys.exc_info()[0],
        )
        logger.error(e)
    conn.commit()
    conn.close()
    return


def updateMaxCatArt(idUser, newMax):
    """
    CATEGORY
    Funzione per update ultimo articolo letto
    """
    conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
    c = conn.cursor()
    try:
        c.execute(
            "update interessi set catLastArticolo = ? where idUser = ?",
            (newMax, int(idUser)),
        )
    except sqlite3.OperationalError as e:
        logger.error(
            "(updateMaxCatArt) Sqlite operational error: {}, newMax: {}, idUser: {} Retrying...".format(
                e, newMax, int(idUser)
            )
        )
    except Exception as e:
        logger.error(
            "(updateMaxCatArt) Eccezione durante la update di catLastArticolo per l'utente "
            + str(idUser),
            sys.exc_info()[0],
        )
        logger.error(e)
    conn.commit()
    conn.close()
    return


def interessiExtractor(updateFlag=True):
    """
    TOPIC
    """
    logger.debug("interessiExtractor inizio...")
    idUserList = []
    topicList = []
    maxList = []
    utentiInteressi = {}
    (idUserList, topicList, maxList) = interessiUtentiExtractor()
    logger.info(f"Liste utenti:{idUserList}, topic {topicList}, maxList {maxList}")
    # Se non ci sono utenti da avvisare torna liste vuote
    if len(idUserList) == 0:
        logger.debug("Utenti vuoti")
        logger.info(f"interessiExtractor ritorna {utentiInteressi}")
        return utentiInteressi
    # Per ciascun utente presente nella tabella interessi
    for idUser, topic, max in zip(idUserList, topicList, maxList):
        logger.debug(f"idUser,topic,max: {idUser},{topic},{max}")
        articoliList = []
        newMax = 0
        (newMax, articoliList) = articoliPerTopic(topic, max)
        logger.debug(f"articoliPerTopic: {articoliList}, newMax {newMax}")
        if len(articoliList) == 0:
            logger.debug(f"Nessun aggiornamento da TOPIC per {idUser}")
            pass
        if (newMax != 0) and (updateFlag):
            updateMaxArt(idUser, newMax)
        logger.debug(f"Associati a {idUser} questi articoli {articoliList}")
        utentiInteressi[idUser] = articoliList
    logger.info(f"interessiExtractor ritorna {utentiInteressi}")
    return utentiInteressi


def sorgentiExtractor(updateFlag=True):
    """
    SORGENTI
    """
    idUserList = []
    topicList = []
    maxList = []
    utentiInteressi = {}
    (idUserList, topicList, maxList) = sorgentiUtentiExtractor()
    logger.info(f"Liste utenti:{idUserList}, topic {topicList}, maxList {maxList}")
    # Se non ci sono utenti da avvisare torna liste vuote
    if len(idUserList) == 0:
        logger.debug(f"sorgentiExtractor ritorna {utentiInteressi}")
        return utentiInteressi
    # Per ciascun utente presente nella tabella interessi
    for idUser, sorgenti, max in zip(idUserList, topicList, maxList):
        logger.debug(f"idUser,sorgenti,max: {idUser},{sorgenti},{max}")
        articoliList = []
        newMax = 0
        if not max:
            max = 0
        (newMax, articoliList) = articoliPerSorgente(sorgenti, max)
        logger.debug(f"newMax,articoliList: {newMax}, {articoliList}")
        if len(articoliList) == 0:
            logger.debug(f"Nessun aggiornamento da SORGENTI per {idUser}")
            pass
        if (newMax != 0) and (updateFlag):
            updateMaxSourceArt(idUser, newMax)
        logger.debug(f"Associati a {idUser} questi articoli {articoliList}")
        utentiInteressi[idUser] = articoliList
    logger.debug(f"sorgentiExtractor ritorna {utentiInteressi}")
    return utentiInteressi


def categorieExtractor(updateFlag=True):
    """
    CATEGORY
    Funzioni principale per le categorie
    """
    idUserList = []
    topicList = []
    maxList = []
    utentiInteressi = {}
    (idUserList, topicList, maxList) = catUtentiExtractor()
    logger.info(f"Liste utenti:{idUserList}, topic {topicList}, maxList {maxList}")
    # Se non ci sono utenti da avvisare torna liste vuote
    if len(idUserList) == 0:
        logger.debug(f"categorieExtractor ritorna {utentiInteressi}")
        return utentiInteressi
    # Per ciascun utente presente nella tabella interessi
    for idUser, sorgenti, max in zip(idUserList, topicList, maxList):
        logger.debug(f"idUser,sorgenti,max: {idUser},{sorgenti},{max}")
        articoliList = []
        newMax = 0
        if not max:
            max = 0
        (newMax, articoliList) = articoliPerCat(sorgenti, max)
        logger.debug(f"newMax,articoliList: {newMax}, {articoliList}")
        if len(articoliList) == 0:
            logger.debug(f"Nessun aggiornamento da CATEGORIE per {idUser}")
            pass
        if (newMax != 0) and (updateFlag):
            updateMaxCatArt(idUser, newMax)
        logger.debug(f"Associati a {idUser} questi articoli {articoliList}")
        utentiInteressi[idUser] = articoliList
    logger.debug(f"categorieExtractor ritorna {utentiInteressi}")
    return utentiInteressi
