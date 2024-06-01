import botutils
from settings import (
    LOGGER,
    MESSAGE_SIZE_LIMIT,
    DEFAULT_FEED,
    BOT_ID,
    escape_markdown,
)
from newsbot_admin_cmd import dbf, lus, bu, uu, lut, ut, ac, af, db
import NNewsDBReader
import NNewsDBExtractor

# Imports from telegram framework python-telegram-bot
from telegram import (
    Update,
)
from telegram.ext import (
    ContextTypes,
    Application,
    CommandHandler,
)
from telegram.error import TelegramError


logger = LOGGER


async def avvisa_admin(context: ContextTypes.DEFAULT_TYPE, mesg):
    """
    Modo per mandare un messaggio a tutti gli amministratori
    """
    admins = botutils.getAdmins()
    logger.debug("Lista amministratori", admins)
    for a in admins:
        await context.bot.send_message(
            chat_id=a, text=escape_markdown(mesg), parse_mode="MarkdownV2"
        )


async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Cmd per avere la lista dei titoli degli articoli relativi ad una sorgente
    passata in modo, anche parziale, come primo argomento
    in un unico messaggio
    """
    try:
        chat_id = update.effective_user.id
        if context.args:
            # Leggo il primo parametro
            default = context.args[0]
        else:
            default = DEFAULT_FEED
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Non hai specificato un parametro di ricerca, vedrai articoli relativi a {default}",
                parse_mode="MarkdownV2",
            )
        messages = NNewsDBReader.dbtitoli_link(defNum=20, defSorgente=default)
        # Metto tutti i messaggi in un messaggio solo
        invio = ""
        for message in messages:
            invio = invio + message
        if not invio:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Mi dispiace ma non ho trovato nessuna fonte con la parola {default}...",
                parse_mode="MarkdownV2",
            )
        if len(invio) > MESSAGE_SIZE_LIMIT:
            await context.bot.send_message(
                chat_id=chat_id,
                text=escape_markdown(invio[:MESSAGE_SIZE_LIMIT]),
                parse_mode="MarkdownV2",
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id, text=escape_markdown(invio), parse_mode="MarkdownV2"
            )
    except Exception as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Cmd to send a message when the command /help is issued.
    """
    user = update.effective_user
    chat_id = user.id
    stringa = ""
    stringa = stringa + "Digita:\n"
    stringa = stringa + botutils.selfhelp()
    adminList = botutils.getAdmins()
    if str(chat_id) in adminList:
        stringa = stringa + botutils.help()
    await context.bot.send_message(
        chat_id=chat_id, text=escape_markdown(stringa), parse_mode="MarkdownV2"
    )
    return


async def feedlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Cmd per lista feed, passare categoria "descrittiva"
    """
    user = update.effective_user
    chat_id = user.id
    feed = ""
    if context.args:
        # Leggo il primo parametro
        feed = context.args[0]
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione /feedlist senza passare la categoria; per vedere le categorie usa il comando /catlist",
            parse_mode="MarkdownV2",
        )
        return
    try:
        invio = ""
        messages = botutils.listFeeds(feed)
        logger.info(messages)
        for message in messages:
            invio = invio + message + "\n"
        if len(invio) > MESSAGE_SIZE_LIMIT:
            await context.bot.send_message(
                chat_id=chat_id,
                text=escape_markdown(invio[:MESSAGE_SIZE_LIMIT]),
                parse_mode="MarkdownV2",
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id, text=escape_markdown(invio), parse_mode="MarkdownV2"
            )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def catlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Lista categorie
    """
    user = update.effective_user
    chat_id = user.id
    try:
        invio = ""
        messages = botutils.listCategories()
        for message in messages:
            invio = invio + message + "\n"
        if len(invio) > MESSAGE_SIZE_LIMIT:
            await context.bot.send_message(
                chat_id=chat_id,
                text=escape_markdown(invio[:MESSAGE_SIZE_LIMIT]),
                parse_mode="MarkdownV2",
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id, text=escape_markdown(invio), parse_mode="MarkdownV2"
            )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Funzione di ricerca sugli articoli
    """
    try:
        chat_id = update.effective_user.id
        if context.args:
            # Leggo il primo parametro
            default = context.args[0]
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Non hai specificato un parametro di ricerca",
                parse_mode="MarkdownV2",
            )
            return
        messages = NNewsDBReader.dbsearch(
            defNum=5, defSearch=default
        )  # Passare defSearch come parametro di ricerca
        if not messages:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Mi dispiace, non ho trovato nulla",
                parse_mode="MarkdownV2",
            )
        else:
            for message in messages:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=escape_markdown(message),
                    parse_mode="MarkdownV2",
                )
    except Exception as e:
        logger.exception(e)
        await context.bot.send_message(chat_id=chat_id, text=format(e))


async def pushme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Aggiorna ricerca parola/e in self mode
    """
    user = update.effective_user
    chat_id = user.id
    topicList = ""
    if len(context.args) > 0:
        if len(context.args) == 1:
            topicList = context.args[0]
        else:
            topicList = "|".join(context.args)
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione /pushme senza passare gli argomenti necessari: la lista delle parole chiavi separati da spazio",
            parse_mode="MarkdownV2",
        )
        return
    try:
        message = botutils.selfUpdateTopicList(chat_id, topicList)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(message), parse_mode="MarkdownV2"
        )
    except Exception as e:
        logger.exception(e)
        await context.bot.send_message(chat_id=chat_id, text=format(e))
    return


async def feedme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Aggiorna feed in self mode
    """
    user = update.effective_user
    chat_id = user.id
    sourceList = ""
    if len(context.args) > 0:
        for x in context.args:
            # Controllo se interi
            try:
                _ = int(x) + 1
            except ValueError:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"Hai chiamato la funzione /feedme con uno dei parametri ({x}) non numerico",
                    parse_mode="MarkdownV2",
                )
                return
        # Come lista
        sourceList = context.args
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione /feedme senza passare gli argomenti necessari: la lista degli id feed separati da spazio",
            parse_mode="MarkdownV2",
        )
        return
    try:
        message = botutils.selfUpdateSourceList(chat_id, sourceList)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(message), parse_mode="MarkdownV2"
        )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Statistiche articoli per feed
    Argomento: numero giorni, default 10
    TODO: gestire meglio il valore limite
    """
    limite = 10
    user = update.effective_user
    chat_id = user.id
    if context.args:
        # Leggo il primo parametro
        limite = context.args[0]
    try:
        messages = botutils.articleStats(chat_id, int(limite))
        # Metto tutti i messaggi in un messaggio solo
        invio = ""
        for message in messages:
            invio = invio + message + "\n"
            if len(invio) > MESSAGE_SIZE_LIMIT:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=escape_markdown(invio),
                    parse_mode="MarkdownV2",
                )
                invio = ""
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(invio), parse_mode="MarkdownV2"
        )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def ll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Last logs
    """
    limite = 10
    user = update.effective_user
    chat_id = user.id
    if context.args:
        # Leggo il primo parametro
        limite = context.args[0]
    try:
        messages = botutils.lastLogs(chat_id, int(limite))
        # Metto tutti i messaggi in un messaggio solo
        invio = ""
        for message in messages:
            # Comandi con _ davano problemi nel parsing Markdown
            invio = invio + message + "\n"
            if len(invio) > MESSAGE_SIZE_LIMIT:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=escape_markdown(invio),
                    parse_mode="MarkdownV2",
                )
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(invio), parse_mode="MarkdownV2"
        )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def au(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Add user (admin function)
    TODO: Controllare implementazione
    """
    user_to_add = nome = cognome = ""
    user = update.effective_user
    chat_id = user.id
    if len(context.args) > 0:
        if len(context.args) > 0:
            # Leggo il primo parametro
            user_to_add = context.args[0]
        if len(context.args) > 1:
            nome = context.args[1]
        if len(context.args) > 2:
            cognome = context.args[2]
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione add user senza passare utente, nome, cognome da aggiungere",
            parse_mode="MarkdownV2",
        )
        return
    try:
        message = botutils.adduser(chat_id, str(user_to_add), str(nome), str(cognome))
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(message), parse_mode="MarkdownV2"
        )
    except ValueError as ve:
        logger.error(ve.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(ve)), parse_mode="MarkdownV2"
        )
    except Exception as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def du(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Delete user (admin function)
    """
    user = update.effective_user
    chat_id = user.id
    user_to_delete = ""
    if context.args:
        # Leggo il primo parametro
        user_to_delete = context.args[0]
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione delete user senza passare l'utente da cancellare",
            parse_mode="MarkdownV2",
        )
        return
    try:
        message = botutils.deluser(chat_id, str(user_to_delete))
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(message), parse_mode="MarkdownV2"
        )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    chat_id = user.id
    try:
        messages = botutils.start(user.id, user.first_name)
        # Metto tutti i messaggi in un messaggio solo
        invio = ""
        for message in messages:
            invio = invio + message + "\n"
            if len(invio) > MESSAGE_SIZE_LIMIT:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=escape_markdown(invio[:MESSAGE_SIZE_LIMIT]),
                    parse_mode="MarkdownV2",
                )
                invio = ""
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(invio), parse_mode="MarkdownV2"
        )
        invio = ""
    except ValueError as e:
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def catme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Assegna interesse alla categoria passata, in self mode
    """
    catList = ""
    user = update.effective_user
    chat_id = user.id
    if len(context.args) > 1:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione /catme con piu' di un parametro",
            parse_mode="MarkdownV2",
        )
        return
    if len(context.args) == 1:
        catList = context.args[0]
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione /catme senza passare la categoria",
            parse_mode="MarkdownV2",
        )
        return
    try:
        message = botutils.selfUpdateCategory(chat_id, catList)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(message), parse_mode="MarkdownV2"
        )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Visualizza configurazione dell'utente in modalità self
    TODO: gestire markdown "_" italics dei messaggi in risposta
    """
    chat_id = update.effective_user.id
    try:
        messages = botutils.showSettings(chat_id)
        invio = ""
        for message in messages:
            invio = invio + message + "\n"
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(invio), parse_mode="MarkdownV2"
        )
    except Exception as e:
        logger.exception(e)
        await context.bot.send_message(chat_id=chat_id, text=format(e))


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    try:
        messages = botutils.listUsers(chat_id)
        # Metto tutti i messaggi in un messaggio solo
        invio = ""
        logger.debug(messages)
        for message in messages:
            invio = invio + message + "\n"
            if len(invio) > MESSAGE_SIZE_LIMIT:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=escape_markdown(invio),
                    parse_mode="MarkdownV2",
                )
                invio = ""
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(invio), parse_mode="MarkdownV2"
        )
    except ValueError as ve:
        logger.exception(ve)
        await context.bot.send_message(chat_id=chat_id, text=format(ve))


async def send_news(context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.debug("Funzione send_news: inizio")
        # Gestione aggiornamenti in push ogni 10 minuti
        aggiornamentiI, aggiornamentiS, aggiornamentiC = {}, {}, {}
        # Raccoglie tutti gli aggiornamenti (per tipologia)
        aggiornamentiI = NNewsDBExtractor.interessiExtractor(updateFlag=True)
        logger.debug(f"Interessi ({len(aggiornamentiI)}): {aggiornamentiI}")
        aggiornamentiS = NNewsDBExtractor.sorgentiExtractor(updateFlag=True)
        logger.debug(f"Sorgenti ({len(aggiornamentiS)}): {aggiornamentiS}")
        aggiornamentiC = NNewsDBExtractor.categorieExtractor(updateFlag=True)
        logger.debug(f"Categorie ({len(aggiornamentiC)}): {aggiornamentiC}")
        # Li unisce per user (key)
        aggiornamenti = {}
        for key in set(
            list(aggiornamentiI.keys())
            + list(aggiornamentiS.keys())
            + list(aggiornamentiC.keys())
        ):
            # Unisce gli aggiornamenti
            logger.debug(f"User key: {key}")
            try:
                aggiornamenti.setdefault(key, []).extend(aggiornamentiI[key])
            except KeyError as ke:
                logger.exception(ke)
                pass
            try:
                aggiornamenti.setdefault(key, []).extend(aggiornamentiS[key])
            except KeyError as ke:
                logger.exception(ke)
                pass
            try:
                aggiornamenti.setdefault(key, []).extend(aggiornamentiC[key])
            except KeyError as ke:
                logger.exception(ke)
                pass
        # Elimina i duplicati tra le news, che potrebbero derivare da criteri diversi
        aggiornamenti[key] = list(dict.fromkeys(aggiornamenti[key]))
        logger.debug(f"Aggiornamenti: {aggiornamenti}")
        for userId in aggiornamenti:
            logger.debug(f"Aggiornamento utente {userId}")
            # Se userId negativo è un gruppo, controllo se ha topic
            topicId = None
            if int(userId) < 0:
                topicId = botutils.get_telegram_topic(userId)
            # Mando al massimo 5 messaggi per utente, se ci sono messaggi da mandare
            if aggiornamenti[userId]:
                for a in aggiornamenti[userId][:5]:
                    logger.debug(f"Aggiornamento a {userId}: {a}")
                    try:
                        if topicId:
                            await context.bot.send_message(
                                chat_id=userId, message_thread_id=topicId, text=a
                            )
                        else:
                            await context.bot.send_message(chat_id=userId, text=a)
                    except TelegramError as tg:
                        logger.exception(tg)
                        botutils.logga(
                            "ERR", userId, userId, "L'utente ha bloccato il bot"
                        )
                        # Cancella user
                        # botutils.deluser('259697154', userId)
                        pass
            else:
                logger.debug(f"Nessun aggiornamento per {userId}...")
    except Exception as e:
        logger.exception(e)
        botutils.logga("ERR", userId, userId, "API exception. Guardare i log")


# TODO: fare main
application = Application.builder().token(BOT_ID).build()
# Per i task periodici
job_queue = application.job_queue
# Ogni 10 minuti (600 secondi)
job_minute = job_queue.run_repeating(send_news, interval=600, first=10)

# Comandi del bot
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help))
application.add_handler(CommandHandler("lu", list_users))
application.add_handler(CommandHandler("dbf", dbf))
application.add_handler(CommandHandler("db", db))
application.add_handler(CommandHandler("feed", feed))
application.add_handler(CommandHandler("search", search))
# Comandi del bot per operatività "self"
application.add_handler(CommandHandler("me", me))
application.add_handler(CommandHandler("pushme", pushme))
application.add_handler(CommandHandler("feedme", feedme))
application.add_handler(CommandHandler("catme", catme))
application.add_handler(CommandHandler("feedlist", feedlist))
application.add_handler(CommandHandler("catlist", catlist))
# Comandi ADMIN del bot
application.add_handler(CommandHandler("bu", bu))
application.add_handler(CommandHandler("uu", uu))
application.add_handler(CommandHandler("lus", lus))
application.add_handler(CommandHandler("lut", lut))
application.add_handler(CommandHandler("ut", ut))
application.add_handler(CommandHandler("au", au))
application.add_handler(CommandHandler("ac", ac))
application.add_handler(CommandHandler("af", af))
application.add_handler(CommandHandler("du", du))
application.add_handler(CommandHandler("ll", ll))
application.add_handler(CommandHandler("stats", stats))
# Bot start polling
application.run_polling()
