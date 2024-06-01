#Generic news updater
###################
#22.12.2018 - First version
#08.01.2019 - Open and close connections multiple times to avoid, as much as possible, OperationalError "DatabaseError: database is locked"
#07.01.2024 - Using path for scrapers in importlib
###################
import sqlite3
import sys
import importlib.util
import os
import settings
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


try:
    conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
    c = conn.cursor()
    today = settings.adesso()
    c.execute("SELECT idSorgente,sorgente,scraperMethod,defUrl,baseUrl,defNum FROM sorgente where scraperMethod is not null")
    table = c.fetchall()
    conn.close()
    # Leggo tutti i dati delle sorgenti disponibili e aggiorno il DB con le news provenienti dai crawlers definiti in scraperMethod
    # for row in c.execute("SELECT idSorgente,sorgente,scraperMethod,defUrl,baseUrl,defNum FROM sorgente where scraperMethod is not null"):
    for row in table:
        idSorgente = row[0]
        sorgente = row[1]
        scraperMethod = row[2]
        defUrl = row[3]
        baseUrl = row[4]
        defNum = row[5]
        logger.info("#################################################################")
        logger.info(f"# Parametri tabella sorgente {idSorgente} - {sorgente} - {scraperMethod} - {defUrl} - {baseUrl} - {defNum}")
        logger.info("#################################################################")
        today = settings.adesso()
        #Se non c'è scraperMethod, non c'è crawler!
        if (scraperMethod):
            module_name, func_name = scraperMethod.rsplit('.',1)
            # Import dinamico del modulo
            try:
                # https://medium.com/@david.bonn.2010/dynamic-loading-of-python-code-2617c04e5f3f
                scrapers_package = os.path.join('..', 'scrapers',module_name+".py")
                spec = importlib.util.spec_from_file_location(module_name, scrapers_package)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mod
                spec.loader.exec_module(mod)                
            except ImportError as ie:
                err = 'ERRORE DI CONFIGURAZIONE TABELLA SORGENTI - Errore durante l''import del modulo - ImportError: '+str(ie)
                logger.error(err)
                conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
                f = conn.cursor()
                f.execute ("UPDATE sorgente SET lastKo = ?, lastError = ? where idSorgente = "+str(idSorgente), (today, err))
                conn.commit()
                conn.close()
                continue
            # Richiamo dinamico della funzione
            try:
                # Valorizzazione del nome funzione
                scraperFunc = getattr(mod, func_name)
            except:
                err = 'ERRORE DI CONFIGURAZIONE TABELLA SORGENTI - Errore nel nome del metodo scraper.Funziona ancora?'
                logger.error(err)
                conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
                f = conn.cursor()
                f.execute ("UPDATE sorgente SET lastKo = ?, lastError = ? where idSorgente = "+str(idSorgente), (today, err))
                conn.commit()
                conn.close()
                continue
            logger.info(today + ">>> Trovato per ["+ sorgente + "] il metodo [" + scraperMethod + "]")
            #Esecuzione dello scraper
            try:
                # Se è stato definito defUrl va utilizzato, poi richiamo della funzione
                if (defUrl):
                    date, titoli, links, testi = scraperFunc(defUrl=defUrl)
                else:
                    date, titoli, links, testi = scraperFunc()
            except:
                err = 'ERRORE NELL''ESECUZIONE del metodo scraper'
                logger.error(err)
                # In caso di errore, memorizzo il KO
                try:
                    conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
                    f = conn.cursor()
                    f.execute ("UPDATE sorgente SET lastKo = ?, lastError = ? where idSorgente = "+str(idSorgente), (today, err))
                    conn.commit()
                    conn.close()
                    continue
                except sqlite3.OperationalError as oe:
                    logger.error("Operational error",oe)
                    pass
            #Se non è ritornato nulla, c'è un problema con il web crawler
            if (date):
                # Se ok, inserisco gli articoli
                tupla = zip(date, titoli, links, testi)
                scartati = 0
                provati = 0
                for t in tupla:
                    try:
                        conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
                        e = conn.cursor()
                        provati = provati + 1
                        e.execute ("INSERT INTO articoli VALUES (null, ?, "+str(idSorgente)+", ?, ?, ? )", t)
                        conn.commit()
                        conn.close()
                    except sqlite3.OperationalError as oe:
                        logger.error("Operational error",oe)
                        pass
                        
                    except sqlite3.IntegrityError:
                        scartati = scartati + 1 
                        pass
                logger.info(f"Provati {provati} di cui scartati {scartati} perche' gia' presenti..." )        
            else:
                err = "ERRORE NELLO SCRAPER: Nessuna notizia dallo scraper. Funziona ancora?"
                logger.error(err)
                try:
                    conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
                    f = conn.cursor()
                    f.execute ("UPDATE sorgente SET lastKo = ?, lastError = ? where idSorgente = "+str(idSorgente), (today, err))
                    conn.commit()
                    conn.close()
                except sqlite3.OperationalError as oe:
                    logger.error("Operational error",oe)
                    pass
                    
        else:
            err = "ERRORE DI CONFIGURAZIONE TABELLA SORGENTI : non trovato writer!!!"
            logger.error(err)
            try:
                conn = sqlite3.connect(settings.burlescoDb, isolation_level=None, timeout=30)
                f = conn.cursor()
                f.execute ("UPDATE sorgente SET lastKo = ?, lastError = ? where idSorgente = "+str(idSorgente), (today, err))
                conn.commit()
                conn.close()
            except sqlite3.OperationalError as oe:
                logger.error("Operational error",oe)
                pass
                
except sqlite3.IntegrityError as ie:
    logger.error('ERRORE DB: IntegrityError',ie)
    pass
except UnicodeEncodeError as uee:
    logger.error('ERRORE NEI CARATTERI: UnicodeEncodeError', uee )
    pass
finally:
    conn.close()
#####
logger.info("-------------------------------")
logger.info("Fine di tutti gli aggiornamenti")