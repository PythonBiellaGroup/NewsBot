import sqlite3
import settings

logger = settings.LOGGER

def dbreader(defDB=settings.burlescoDb, defNum=10, defLung=settings.ARTICLE_TEXT_SIZE_LIMIT):
    '''
    Ricerca senza filtri, ordinato per data desc
    '''
    msg_list = []
    messaggio = ""
    conn = sqlite3.connect(defDB)
    c = conn.cursor()
    for row in c.execute('SELECT a.data, s.sorgente, a.titolo, a.link, a.testo FROM articoli a, categoria c, sorgente s where s.idCategoria = c.idCategoria and s.idSorgente = a.idSorgente ORDER BY data DESC LIMIT ?', (defNum,)):
        data = row[0]
        fonte = row[1]
        titolo = row[2]
        link = row[3]
        testo = row[4]
        if len(testo) > defLung:
            testo = testo[0:defLung] + "..."        
        messaggio = f"[{data}] da ({fonte})\n{titolo}\n\n "
        messaggio = messaggio + testo
        messaggio = messaggio + f"\n{link}" 
        msg_list.append(messaggio)
    conn.close()
    return msg_list
    

def dbsearch(defDB=settings.burlescoDb, defNum=10, defSearch="killer", defLung=500):
    '''
    Ricerca filtrando per titolo
    '''
    stringList = []
    stringa = ""
    conn = sqlite3.connect(defDB)
    c = conn.cursor()
    for row in c.execute('SELECT a.data, s.sorgente, a.titolo, a.link, a.testo FROM articoli a, categoria c, sorgente s where s.idCategoria = c.idCategoria and s.idSorgente = a.idSorgente and a.titolo like ?ORDER BY data DESC LIMIT ?', ( "%"+defSearch+"%", defNum)):
        data = row[0]
        fonte = row[1]
        titolo = row[2]
        link = row[3]
        testo = row[4]
        if len(testo) > defLung:
            testo = testo[0:defLung] + "..."
        stringa = fonte + " - "+ data+":\n" + titolo + "\n" + link + "\n\n"
        stringa = stringa + testo
        stringList.append(stringa)
    conn.close()
    return stringList    


def dbfonte(defDB=settings.burlescoDb, defNum=10, defSearch="help", defLung=500):
    '''
    Ricerca filtrando per fonte / source
    '''
    stringList = []
    stringa = ""
    conn = sqlite3.connect(defDB)
    c = conn.cursor()
    for row in c.execute('SELECT a.data, s.sorgente, a.titolo, a.link, a.testo FROM articoli a, categoria c, sorgente s where s.idCategoria = c.idCategoria and s.idSorgente = a.idSorgente and s.sorgente like ? ORDER BY data DESC LIMIT ?', ( "%"+defSearch+"%", defNum)):
        data = row[0]
        fonte = row[1]
        titolo = row[2]
        link = row[3]
        testo = row[4]
        if len(testo) > defLung:
            testo = testo[0:defLung] + "..."        
        stringa = "["+data+"] dal sito (" + fonte + ")\n" + titolo + "\n\n"
        stringa = stringa + testo
        stringa = stringa + "\n Per approfondimenti: " + link
        stringList.append(stringa)
    conn.close()
    return stringList    
    

def dbsorgente(defDB=settings.burlescoDb, defNum=10, defSorgente=1, defLung=500):
    stringList = []
    stringa = ""
    conn = sqlite3.connect(defDB)
    c = conn.cursor()
    for row in c.execute('SELECT a.data, s.sorgente, a.titolo, a.link, a.testo FROM articoli a, categoria c, sorgente s where s.idCategoria = c.idCategoria and s.idSorgente = a.idSorgente and s.idSorgente = ? ORDER BY data DESC LIMIT ?', ( defSorgente, defNum)):
        data = row[0]
        fonte = row[1]
        titolo = row[2]
        link = row[3]
        testo = row[4]
        if len(testo) > defLung:
            testo = testo[0:defLung] + "..."        
        stringa = "["+data+"] dal sito (" + fonte + ")\n" + titolo + "\n\n"
        stringa = stringa + testo
        stringa = stringa + "\n Per approfondimenti: " + link
        stringList.append(stringa)
    conn.close()
    return stringList        
    

def dbtitoli(defDB=settings.burlescoDb, defNum=100, defSorgente="stampa"):
    stringList = []
    stringa = ""
    conn = sqlite3.connect(defDB)
    c = conn.cursor()
    for row in c.execute('SELECT a.data, a.titolo FROM articoli a, categoria c, sorgente s where s.idCategoria = c.idCategoria and s.idSorgente = a.idSorgente and s.sorgente like ? ORDER BY data DESC LIMIT ?', ( "%"+defSorgente+"%", defNum)):
        data = row[0]
        titolo = row[1]        
        stringa = "["+data+"] " + titolo + "\n"
        stringList.append(stringa)
    conn.close()
    return stringList            
    
    
def dbtitoli_link(defDB=settings.burlescoDb, defNum=100, defSorgente="stampa"):
    stringList = []
    stringa = ""
    conn = sqlite3.connect(defDB)
    c = conn.cursor()
    for row in c.execute('SELECT a.data, a.titolo, a.link FROM articoli a, categoria c, sorgente s where s.idCategoria = c.idCategoria and s.idSorgente = a.idSorgente and s.sorgente like ? ORDER BY data DESC LIMIT ?', ( "%"+defSorgente+"%", defNum)):
        data = row[0]
        titolo = row[1]
        link = row[2]
        stringa = data+":\n" + titolo + "\n" + link + "\n\n"
        stringList.append(stringa)
    conn.close()
    return stringList