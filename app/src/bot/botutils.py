#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import datetime
import pytz
import sqlite3
import settings

logger = settings.LOGGER


def starthelp(name):
    stringa = ""
    stringa = stringa + f"Benvenuto {name},\n"
    stringa = (
        stringa
        + "Questo e' un bot sperimentale e dimostrativo, sviluppato a scopo didattico, "
    )
    stringa = (
        stringa
        + "che ti permette di filtrare e selezionare le news dei siti che scegli di monitorare.\n\n"
    )
    stringa = stringa + "I siti sono chiamati anche feed e sono divisi in categorie.\n"
    stringa = stringa + "Usa il comando /catlist per vedere le categorie.\n\n"
    stringa = (
        stringa
        + "Se desideri ricevere le notizie contenenti una o più parole, indipendentemente dal sito o dalla categoria, "
    )
    stringa = (
        stringa
        + "con il comando /pushme seguito da una o più parole, imposterai le notifiche delle notizie aventi la o le parole nel titolo.\n"
    )
    stringa = (
        stringa
        + "Ad esempio se scrivi '/pushme pizza', riceverai le notizie aventi la parola 'pizza' nel titolo.\n\n"
    )
    stringa = stringa + "Se desideri ricevere TUTTE le notizie da uno o più siti, "
    stringa = (
        stringa
        + "con il comando /feedme seguito da uno o più numeri corrispondenti a feed di notizie, imposterai le notifiche relative alle fonti di notizie che vuoi ricevere. "
    )
    stringa = (
        stringa
        + "Ad esempio se scrivi '/feedme 1', riceverai le notizie dal sito impostato come feed 1.\n\n"
    )
    stringa = (
        stringa
        + "Con il comando /catme seguito dal nome di una categoria, imposterai le notifiche relative a TUTTE le fonti di quella determinata categoria.\n"
    )
    stringa = (
        stringa
        + "Ad esempio, se esiste la categoria BIELLA, scrivendo '/catme biella', riceverai le notizie di tutti i siti aventi come categoria Biella.\n\n"
    )
    stringa = (
        stringa
        + "Usa il comando /feedlist seguito dal nome categoria per vedere l'elenco delle fonti e numero corrispondente. Ad esempio '/feedlist biella'.\n\n"
    )
    stringa = (
        stringa
        + "Usa il comando /help per vedere la lista dei comandi e il comando /start per rileggere questa spiegazione.\n\n"
    )
    stringa = (
        stringa
        + "In ogni momento puoi usare il comando /me per vedere le tue impostazioni in tempo reale.\n"
    )
    return stringa


def selfhelp():
    stringa = ""
    stringa = stringa + "\n➡️ GESTIONE DATI PERSONALI E CONFIGURAZIONI NEWS\n"
    stringa = stringa + "/me - mostra le configurazioni dell'utente\n"
    stringa = (
        stringa
        + "/pushme + lista parole chiavi separate da spazio (es. /pushme Biella lana)\n"
    )
    stringa = (
        stringa
        + "/feedme + lista id feed separati da spazio (es. /feedme 1 2); /feedlist per avere la lista\n"
    )
    stringa = (
        stringa
        + "/catme + categoria per ricevere tutte le news di quella categoria (es. /catme Vercelli); /catlist per avere la lista\n"
    )
    stringa = stringa + "\n➡️ UTILI\n"
    stringa = stringa + "/feedlist - per avere la lista di id feed\n"
    stringa = stringa + "/catlist - per avere la lista delle categorie dei feed\n"
    stringa = stringa + "\n➡️ FUNZIONI DI RICERCA\n"
    stringa = (
        stringa
        + "/feed N - per avere le ultime news relativa al feed N (es. /feed stampa); /feedlist per avere la lista\n"
    )
    stringa = (
        stringa
        + "/search X - per avere i titoli delle ultime news contente la parola X (es. /search Trump)\n"
    )
    return stringa


def help():
    stringa = ""
    stringa = stringa + "\n➡️ ADMIN CMDs - UTENTI\n"
    stringa = stringa + "/lu - List Users\n"
    stringa = stringa + "/au - Add User (user)\n"
    stringa = stringa + "/du - Del User (user)\n"
    stringa = stringa + "/bu - Ban User (user)\n"
    stringa = stringa + "/uu - UnBan User (user)\n"
    stringa = stringa + "\n➡️ ADMIN CMDs - INTERESSI\n"
    stringa = stringa + "/ut - User Topic List (user topic1 topic2 ... topicN)\n"
    stringa = stringa + "/lus - List User Sources (user opt)\n"
    stringa = stringa + "/lut - List User Topics (user opt)\n"
    stringa = stringa + "/ac nomecategory - Add category nomecategory\n"
    stringa = (
        stringa + "/af nomecategory nomefeeed - Add feed nomefeeed into nomecategory\n"
    )
    stringa = stringa + "\n➡️ ADMIN CMDs - LOGS\n"
    stringa = stringa + "/ll - Last logs (limit)\n"
    stringa = (
        stringa + "/stats - Statistics articoli per sorgente (dayslimit, default 10)\n"
    )
    stringa = stringa + "\n➡️ ADMIN DB\n"
    stringa = (
        stringa
        + "/dbf (sorgente) - Lista ultimi articoli per la sorgente specificata \n"
    )
    stringa = stringa + "/db - Lista ultimi articoli inseriti\n"
    stringa = (
        stringa + "/stats - Statistics articoli per sorgente (dayslimit, default 10)\n"
    )
    return stringa


def adesso():
    """Funzioni per la gestione degli orari"""
    st = datetime.datetime.now(pytz.timezone(settings.BOTTIMEZONE)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    return st


def minuto():
    """Funzioni per la gestione degli orari"""
    st = datetime.datetime.now(pytz.timezone(settings.BOTTIMEZONE)).strftime("%M")
    return st


def logga(logType, idChat, idUser, message):
    """
    Creazione elementi in tabella logs:
    - il timestamp nel formato dd-mm-aaaa hh:mm:ss messo all'inizio della riga e' generato dalla funzione adesso()
    - ci sono tre tipi di messaggi di log:
    0 = [INF] informazione
    1 = [AVV] avviso
    2 = [ERR] errore
    cosi' da poter filtrare il log alla ricerca di errori senza vedere tutti i messaggi meno gravi
    """
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    now = adesso()
    t = (now, logType, idChat, idUser, message)
    try:
        c.execute("INSERT INTO logs VALUES (null, ?, ?, ?, ?, ? )", t)
    except Exception as e:
        logger.error(
            "Eccezione durante la INSERT con questi parametri", t, sys.exc_info()[0]
        )
        logger.error(e)
    conn.commit()
    return


def lastLogs(sender, numLogs=10):
    """Lista ultimi logs"""
    logList = []
    logList.append("*ULTIMI LOGS*")
    adminList = getAdmins()
    if any(str(sender) in item for item in adminList):
        # Utente abilitato
        logger.info(f"Utente {sender} abilitato")
    else:
        raise ValueError("Visualizzazione log non abilitata")
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    try:
        for row in c.execute(
            "SELECT a.data, a.logType, a.idUser, b.nome, a.message FROM logs a, utenti b where b.idUser = a.idUser ORDER BY data DESC LIMIT ?",
            (numLogs,),
        ):
            logList.append(
                row[0] + ", " + row[1] + ", " + row[2] + "-" + row[3] + ", " + row[4]
            )
    except Exception as e:
        logger.error("Eccezione durante la SELECT", sys.exc_info()[0])
        logger.error(e)
    conn.close()
    return logList


def articleStats(sender, numDays=10):
    """Statistiche sorgenti con più articoli"""
    try:
        str(numDays)
    except Exception as e:
        logger.error("Eccezione durante la conversione parametro", sys.exc_info()[0])
        logger.error("Eccezione durante la conversione parametro", e)
        raise ValueError("Parametro non corretto")
    statsList = []
    statsList.append("*STATISTICHE ARTICOLI ULTIMI " + str(numDays) + " GIORNI*")
    adminList = getAdmins()
    if any(str(sender) in item for item in adminList):
        # Utente abilitato
        logger.info(f"Utente {sender} abilitato")
    else:
        raise ValueError("Funzione non abilitata")
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    queryStr = (
        "select count(*), b.sorgente from articoli a, sorgente b where a.idSorgente = b.idSorgente and a.data > date('now','-"
        + str(numDays)
        + " day') group by a.idSorgente order by count(*) desc"
    )
    try:
        for row in c.execute(queryStr):
            statsList.append(str(row[0]) + ", " + row[1])
    except Exception as e:
        logger.error(f"(articleStats) Eccezione durante la SELECT; {sys.exc_info()[0]}")
        logger.error(e)
    conn.close()
    return statsList


def listUsers(sender):
    """Lista utenti da DB"""
    logger.debug(f"Lista utenti richiamata da {sender}")
    userList = []
    userList.append("*LISTA UTENTI*")
    logger.debug(sender)
    adminList = getAdmins()
    logger.debug(adminList)
    if any(str(sender) in item for item in adminList):
        logger.debug(f"Utente {sender} abilitato")
    else:
        raise ValueError("Operazione lista utenti non abilitata")
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    try:
        for row in c.execute(
            "SELECT idUser, nome, cognome, isAdmin, dataNascita, dataPrimoUtilizzo, dataUltimoUtilizzo FROM utenti"
        ):
            # dataNascita row[4] è NULL e crea TypeError
            # userList.append(row[0] + ", " + row[1] + ", " + row[2] + ", " + str(row[3])+ ", " + row[4]+ ", " + row[5]+ ", " + row[6])
            logger.debug(
                f"Risultato query: {row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[5]}, {row[6]}"
            )
            userList.append(
                row[0]
                + ", "
                + row[1]
                + ", "
                + row[2]
                + ", "
                + str(row[3])
                + ", "
                + row[5]
                + ", "
                + row[6]
            )
    except Exception as e:
        logger.error("Eccezione durante la SELECT", sys.exc_info()[0])
        logger.error(e)
    conn.close()
    return userList


def deluser(sender, user_to_del):
    """Cancellazione utente"""
    logger.debug(f"Cancellazione utente richiamata da {sender} per {user_to_del}")
    adminList = getAdmins()
    if str(sender) not in adminList:
        raise ValueError("Cancellazione di utenti non abilitata")
    if ControllaUtenteDb(user_to_del):
        conn = sqlite3.connect(settings.burlescoDb)
        c = conn.cursor()
        try:
            c.execute("DELETE FROM utenti WHERE idUser = ?", (user_to_del,))
            conn.commit()
        except Exception as e:
            logger.error("Eccezione durante DELETE", sys.exc_info()[0])
            logger.error(e)
        conn.close()
        return f"Utente {user_to_del} eliminato"
    return f"Utente {user_to_del} non presente"


def banuser(sender, userToBan):
    """Banna utente"""
    logger.debug(f"Ban utente richiamata da {sender} per {userToBan}")
    adminList = getAdmins()
    if str(sender) not in adminList:
        raise ValueError("Ban utenti non abilitata")
    if ControllaUtenteDb(userToBan):
        conn = sqlite3.connect(settings.burlescoDb)
        c = conn.cursor()
        try:
            c.execute("UPDATE utenti SET banned=1 WHERE idUser = ?", (userToBan,))
            conn.commit()
        except Exception as e:
            logger.error("Eccezione durante UPDATE", sys.exc_info()[0])
            logger.error(e)
        conn.close()
        return f"Utente {userToBan} bannato"
    return f"Utente {userToBan} non presente"


def unbanuser(sender, user_to_unban):
    """UnBan utente"""
    logger.debug(f"UnBan utente richiamata da {sender} per {user_to_unban}")
    adminList = getAdmins()
    if str(sender) not in adminList:
        raise ValueError("UnBan utenti non abilitata")
    if ControllaUtenteDb(user_to_unban):
        conn = sqlite3.connect(settings.burlescoDb)
        c = conn.cursor()
        try:
            c.execute("UPDATE utenti SET banned=0 WHERE idUser = ?", (user_to_unban,))
            conn.commit()
        except Exception as e:
            logger.error("Eccezione durante UPDATE", sys.exc_info()[0])
            logger.error(e)
        conn.close()
        return f"Utente {user_to_unban} sbannato"
    return f"Utente {user_to_unban} non presente"


def start(userToAdd, nomeToAdd, cognomeToAdd=""):
    """Funzione di inizio bot e accoglienza"""
    messages = []
    if ControllaUtenteDb(userToAdd):
        # Utente già precedentemente iscritto
        if isBanned(userToAdd):
            messages.append("Spiacente, non sei autorizzato all'utilizzo del bot...")
        else:
            messages.append(starthelp(nomeToAdd))
    else:
        ora = adesso()
        # Utente nuovo
        conn = sqlite3.connect(settings.burlescoDb)
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO utenti VALUES (?, ?, ?, 0, null, ?, ?,0)",
                (userToAdd, nomeToAdd, cognomeToAdd, ora, ora),
            )
            conn.commit()
        except Exception as e:
            logger.error("Eccezione durante INSERT", sys.exc_info()[0])
            logger.error(e)
        conn.close()
        messages.append(starthelp(nomeToAdd))
    return messages


def insertCategory(sender, category):
    """Inserimento CATEGORY"""
    strId = returnString = ""
    adminList = getAdmins()
    category = category.upper()
    if str(sender) not in adminList:
        raise ValueError("Inserimento category non abilitato")
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    try:
        # print(category)
        c.execute("INSERT INTO categoria VALUES (null, ?)", (category,))
        conn.commit()
        d = conn.cursor()
        for row in d.execute(
            "SELECT idCategoria FROM categoria WHERE categoria = ? ", (category,)
        ):
            strId = str(row[0])
        if not strId:
            returnString = "Categoria non inserita"
            return returnString
    except Exception as e:
        logger.error("Eccezione durante INSERT", sys.exc_info()[0])
        logger.error(e)
        returnString = "Categoria non inserita per problemi tecnici. Controllare i log"
        return returnString
    conn.close()
    returnString = "Categoria [" + category + "] inserita con idCategoria" + strId
    return returnString


def insertFeed(sender, category, feed):
    """Inserimento FEED"""
    returnString = idSorgente = ""
    adminList = getAdmins()
    category = category.upper()
    if str(sender) not in adminList:
        raise ValueError("Inserimento feed non abilitato")
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    try:
        for row in c.execute(
            "SELECT idCategoria FROM categoria WHERE categoria = ? ", (category,)
        ):
            idcategory = row[0]
        if not idcategory:
            returnString = "Categoria non trovata"
            conn.close()
            return returnString
        d = conn.cursor()
        d.execute("INSERT INTO sorgente VALUES (null, ?, ?)", (idcategory, feed))
        conn.commit()
        e = conn.cursor()
        for row in e.execute(
            "SELECT idSorgente FROM sorgente WHERE sorgente = ? ", (feed,)
        ):
            idSorgente = str(row[0])
    except Exception as e:
        logger.error("Eccezione durante INSERT", sys.exc_info()[0])
        logger.error(e)
        returnString = "Feed non inserito per problemi tecnici. Guardare i log"
        conn.close()
        return returnString
    conn.close()
    returnString = "Feed [" + feed + "] inserita con idSorgente " + str(idSorgente)
    return returnString


def adduser(sender, userToAdd, nomeToAdd="", cognomeToAdd=""):
    """Inserimento forzoso AMMINISTRATIVO nuovo utente"""
    adminList = getAdmins()
    if str(sender) not in adminList:
        raise ValueError("Inserimento di nuovi utenti non abilitato")
    if ControllaUtenteDb(userToAdd):
        return "Utente già abilitato"
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO utenti VALUES (?, ?, ?, 0, null, null, null,0)",
            (userToAdd, nomeToAdd, cognomeToAdd),
        )
        conn.commit()
    except Exception as e:
        logger.error("Eccezione durante INSERT", sys.exc_info()[0])
        logger.error(e)
    conn.close()
    return "Utente inserito"


def listUserSources(sender, user=None):
    """Funziona di lista utenti / FEEDs per amministratore"""
    topics = []
    topics.append("*LISTA INTERESSI*")
    adminList = getAdmins()
    if str(sender) not in adminList:
        raise ValueError("Lista topics non abilitata")
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    try:
        for row in c.execute(
            "SELECT a.idUser, c.nome, c.cognome, b.sorgente FROM interessi a, sorgente b, utenti c where b.idSorgente = a.sourceList and a.idUser = c.idUser"
        ):
            # Se user valorizzato, restituisce le preferenze solo di quello
            if user:
                if user == row[0]:
                    topics.append(row[1] + ", " + row[2] + ", " + row[3])
            # Altrimenti tutte
            else:
                topics.append(row[1] + ", " + row[2] + ", " + row[3])
    except Exception as e:
        logger.error("Eccezione durante la SELECT", sys.exc_info()[0])
        logger.error(e)
    conn.close()
    return topics


def get_telegram_topic(user_id):
    idTopic = None
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    try:
        c.execute(
            "SELECT b.idTopic FROM utenti b where b.idUser = ? and b.idTopic IS NOT NULL",
            (user_id,),
        )
        data = c.fetchall()
        if len(data) > 0:
            idTopic = data[0][0]
    except Exception as e:
        logger.error("Eccezione", sys.exc_info()[0])
        logger.error(f"Eccezione: {e}")
        conn.close()
    conn.close()
    return idTopic


def selfUpdateCategory(sender, category):
    logger.debug(category)
    if not category:
        raise ValueError("E" " richiesta la categoria in input")
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    idcategory = ""
    try:
        c.execute(
            "SELECT idCategoria FROM categoria WHERE categoria = ? COLLATE NOCASE",
            (category,),
        )
        data = c.fetchall()
        if len(data) == 0:
            returnString = "Categoria non trovata"
            conn.close()
            raise ValueError(returnString)
        else:
            idcategory = data[0][0]
            # print(idcategory)
        d = conn.cursor()
        try:
            d.execute("SELECT catList FROM interessi where idUser = ?", (sender,))
            exists = d.fetchall()
            if exists:
                d.execute(
                    "UPDATE interessi SET catList = ?, catLastArticolo=0 where idUser = ?",
                    (str(idcategory), str(sender)),
                )
                conn.commit()
            else:
                d.execute(
                    "INSERT INTO interessi VALUES (null, ?, null, 0, null, 0, ?, 0)",
                    (sender, idcategory),
                )
                conn.commit()
        except Exception as e:
            logger.error("Eccezione durante UPDATE o INSERT", sys.exc_info()[0])
            logger.error(e)
            conn.close()
            return "Eccezione durante aggiornamento categoria per l'utente " + str(
                sender
            )
    except ValueError:
        conn.close()
        return returnString
    except Exception as e:
        logger.error("Eccezione durante UPDATE o INSERT", sys.exc_info()[0])
        logger.error(e)
        conn.close()
        return "Eccezione durante aggiornamento categoria per l'utente " + str(sender)
    conn.close()
    return "Aggiornamento categoria effettuato con successo"


def listFeeds(category):
    """Funzione di lista FEEDs"""
    if not category:
        raise ValueError("E" " richiesta la categoria in input")
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    feeds = []
    feeds.append(f"*LISTA FEEDS per la categoria {category}*")
    feeds.append("(Formato: numero da utilizzare per /feedme, nome feed)")
    try:
        c.execute(
            "SELECT a.idSorgente, a.sorgente FROM sorgente a, categoria b where b.idCategoria = a.idCategoria and b.categoria = ? COLLATE NOCASE order by b.categoria",
            (category,),
        )
        exists = c.fetchall()
        if exists:
            for row in exists:
                feeds.append(str(row[0]) + ", " + row[1])
        else:
            raise ValueError("Nessun feed per la categoria " + category)
    except Exception as e:
        logger.error("Eccezione durante la SELECT", sys.exc_info()[0])
        logger.error(e)
    conn.close()
    return feeds


def listCategories():
    """Funziona di lista categorie"""
    cats = []
    cats.append("*LISTA CATEGORIE FEED*")
    cats.append(
        "(Formato: categoria, seguito, tra parentesi da quanti feeds ci sono nella categoria)"
    )
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    try:
        for row in c.execute(
            "SELECT categoria, count(a.idSorgente) FROM categoria b, sorgente a where a.idCategoria = b.idCategoria group by categoria order by b.categoria"
        ):
            cats.append(row[0] + " (" + str(row[1]) + ")")
    except Exception as e:
        logger.error("Eccezione durante la SELECT", sys.exc_info()[0])
        logger.error(e)
    conn.close()
    return cats


def listUserTopics(sender, user=None):
    """
    Funziona di lista parole chiavi da parte dell'amministratore
    """
    topics = []
    topics.append("*LISTA ARGOMENTI*")
    adminList = getAdmins()
    if str(sender) not in adminList:
        raise ValueError("Lista topics non abilitata")
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    try:
        for row in c.execute(
            "SELECT a.idUser, c.nome, c.cognome, a.topicList FROM interessi a, utenti c where a.idUser = c.idUser"
        ):
            # Se user valorizzato, restituisce le preferenze solo di quello
            if user:
                if user == row[0]:
                    topics.append(row[1] + ", " + row[2] + ", " + row[3])
            # Altrimenti tutte
            else:
                topics.append(row[1] + ", " + row[2] + ", " + row[3])
    except Exception as e:
        logger.error("Eccezione durante la SELECT", sys.exc_info()[0])
        logger.error(e)
    conn.close()
    return topics


def updateTopicList(sender, user, topicList):
    """
    Funzione di aggiornamento parole chiavi da parte dell'amministratore
    """
    adminList = getAdmins()
    if str(sender) not in adminList:
        raise ValueError("Non sei abilitato all" "aggiornamento topics")
    if not ControllaUtenteDb(user):
        raise ValueError("Utente " + str(user) + " non abilitato")
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    try:
        c.execute("SELECT topicList FROM interessi where idUser = ?", (user,))
        exists = c.fetchall()
        if exists:
            c.execute(
                "UPDATE interessi SET topicList = ?, lastArticolo=0 where idUser = ?",
                (topicList, str(user)),
            )
            conn.commit()
        else:
            c.execute(
                "INSERT INTO interessi VALUES (null, ?, ?, 0, null, 0)",
                (user, topicList),
            )
            conn.commit()
    except Exception as e:
        logger.error("Eccezione durante UPDATE o INSERT", sys.exc_info()[0])
        logger.error(e)
        return "Eccezione durante aggiornamento interessi per l'utente " + str(user)
    conn.close()
    return "Topics aggiornati per l'utente " + str(user)


def showSettings(sender):
    """Settings in self mode"""
    shsets = []
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    try:
        for row in c.execute(
            "SELECT b.idUser, b.nome, b.cognome, b.dataPrimoUtilizzo, b.dataUltimoUtilizzo, a.topicList, a.sourceList, a.catList FROM interessi a, utenti b where b.idUser = a.idUser and b.idUser = ?",
            (sender,),
        ):
            idUser = str(row[0])
            nome = row[1]
            # cognome = row[2]
            dpu = row[3]
            duu = row[4]
            topicList = row[5]
            sourceList = row[6]
            catList = row[7]
            if nome:
                shsets.append("*CONFIGURAZIONI UTENTE " + idUser + " (" + nome + ")*")
            if dpu:
                shsets.append("DATA PRIMO UTILIZZO: " + dpu)
            if duu:
                shsets.append("DATA ULTIMO UTILIZZO: " + duu)
            if topicList:
                shsets.append("PAROLE IN PUSH: " + topicList)
            if sourceList:
                shsets.append("FEEDS IN PUSH:")
                # print(sourceList)
                e = conn.cursor()
                # Dinamic binding is complicated
                fstring = (
                    "select b.categoria, a.sorgente from sorgente a, categoria b where a.idCategoria = b.idCategoria and a.idSorgente in ("
                    + sourceList
                    + ")"
                )
                try:
                    for frow in e.execute(fstring):
                        shsets.append(frow[0] + "," + frow[1])
                except Exception as e:
                    logger.error(
                        "(showSettings) Eccezione durante SELECT", sys.exc_info()[0]
                    )
                    logger.error(e)
            if catList:
                shsets.append("CATEGORIA IN PUSH:")
                f = conn.cursor()
                fstring = (
                    "select categoria from categoria where idCategoria in ("
                    + catList
                    + ")"
                )
                # print(fstring)
                try:
                    for frow in f.execute(fstring):
                        shsets.append(frow[0])
                except Exception as e:
                    logger.error(
                        "(showSettings) Eccezione durante SELECT", sys.exc_info()[0]
                    )
                    logger.error(e)
    except Exception as e:
        logger.error("(showSettings) Eccezione durante SELECT", sys.exc_info()[0])
        logger.error(e)
    conn.close()
    return shsets


def selfUpdateTopicList(sender, topicList):
    """Funziona di aggiornamento parole chiavi da parte dell'utente stesso"""
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    try:
        c.execute("SELECT topicList FROM interessi where idUser = ?", (sender,))
        exists = c.fetchall()
        if exists:
            c.execute(
                "UPDATE interessi SET topicList = ?, lastArticolo=0 where idUser = ?",
                (topicList, str(sender)),
            )
            conn.commit()
        else:
            c.execute(
                "INSERT INTO interessi VALUES (null, ?, ?, 0, null, 0, null, 0)",
                (sender, topicList),
            )
            conn.commit()
    except Exception as e:
        logger.error("Eccezione durante UPDATE o INSERT", sys.exc_info()[0])
        logger.error(e)
        return "Eccezione durante aggiornamento interessi per l'utente " + str(sender)
    conn.close()
    return "Aggiornamento effettuato con successo"


def selfUpdateSourceList(sender, sourceList):
    """Funziona di aggiornamento FEED da parte dell'utente stesso"""
    conn = sqlite3.connect(settings.burlescoDb)
    # sourceList è una lista
    c = conn.cursor()
    try:
        # Controlla se i sorgenti specificati esistono...
        # Costruisco la query in base al numero di elementi in lista
        placeholder = "?"  # For SQLite. See DBAPI paramstyle.
        placeholders = ", ".join(placeholder for unused in sourceList)
        # print(placeholders)
        queryStr = (
            "SELECT idSorgente FROM sorgente WHERE idSorgente in (%s)" % placeholders
        )
        # print(queryStr)
        c.execute(queryStr, tuple(sourceList))
        data = c.fetchall()
        # print(len(data))
        # print(len(sourceList))
        if len(data) == 0:
            returnString = (
                "Sorgente/i non trovata/e. Controlla gli id passati come parametro"
            )
            conn.close()
            raise ValueError(returnString)
        elif len(data) != len(sourceList):
            returnString = "Non tutti le sorgenti sono state trovate. Controlla uno per uno gli id passati come parametri"
            conn.close()
            raise ValueError(returnString)
        else:
            try:
                # idcategory = data[0][0]

                sourceListStr = ",".join(sourceList)
                # print(sourceListStr)
                e = conn.cursor()
                # Controlla se l'utente ha già qualche interesse
                e.execute(
                    "SELECT sourceList FROM interessi where idUser = ?", (sender,)
                )
                exists = e.fetchall()
                if exists:
                    e.execute(
                        "UPDATE interessi SET sourceList = ?, sourceLastArticolo=0 where idUser = ?",
                        (sourceListStr, str(sender)),
                    )
                    conn.commit()
                else:
                    e.execute(
                        "INSERT INTO interessi VALUES (null, ?, null, 0, ?, 0, null, 0)",
                        (sender, sourceListStr),
                    )
                    conn.commit()
            except Exception as e:
                logger.error(
                    "(selfUpdateSourceList) Eccezione durante UPDATE o INSERT",
                    sys.exc_info()[0],
                )
                logger.error(e)
                return "Eccezione durante aggiornamento feed per l'utente " + str(
                    sender
                )
    except ValueError:
        conn.close()
        return returnString
    except Exception as e:
        logger.error(
            "(selfUpdateSourceList) (esterna) Eccezione durante UPDATE o INSERT",
            sys.exc_info()[0],
        )
        logger.error(e)
        return "Eccezione durante aggiornamento feed per l'utente " + str(sender)
    conn.close()
    return "Aggiornamento effettuato con successo"


def ControllaUtenteDb(userId):
    """Controlla se l'utente in input è abilitato e aggiorna date visita"""
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    idUser = ""
    utente_abilitato = False
    for row in c.execute(
        "SELECT idUser,dataPrimoUtilizzo,dataUltimoUtilizzo FROM utenti where idUser = ?",
        (userId,),
    ):
        idUser = row[0]
        dataPrimoUtilizzo = row[1]
        dataUltimoUtilizzo = row[2]
    if len(idUser) > 0:
        utente_abilitato = True
        dataUltimoUtilizzo = adesso()
        if not dataPrimoUtilizzo:
            dataPrimoUtilizzo = dataUltimoUtilizzo
        # Update ultima visita
        try:
            c.execute(
                "UPDATE utenti set dataPrimoUtilizzo = ?, dataUltimoUtilizzo = ? where idUser = ?",
                (dataPrimoUtilizzo, dataUltimoUtilizzo, userId),
            )
            conn.commit()
        except Exception as e:
            logger.error("Eccezione durante update", sys.exc_info()[0])
            logger.error(e)
    # Chiusura e uscita
    conn.close()
    return utente_abilitato


def isBanned(idUser):
    """
    IdUser è bannato?
    """
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    banned = 0
    try:
        for row in c.execute("SELECT banned FROM utenti where idUser = ?", (idUser,)):
            banned = row[0]
    except Exception as e:
        logger.error("(isBanned) Eccezione durante SELECT", sys.exc_info()[0])
        logger.error(e)
    conn.close()
    if banned:
        if banned == 1:
            return True
        else:
            return False
    else:
        return False


def getAdmins():
    """Restituisce la lista degli amministratori"""
    conn = sqlite3.connect(settings.burlescoDb)
    c = conn.cursor()
    adminList = []
    try:
        for row in c.execute("SELECT idUser FROM utenti where isAdmin = 1"):
            adminList.append(row[0])
    except Exception as e:
        logger.error("(getAdmins) Eccezione durante SELECT", sys.exc_info()[0])
        logger.error(e)
    conn.close()
    return adminList
