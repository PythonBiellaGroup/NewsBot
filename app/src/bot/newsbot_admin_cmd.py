import botutils
import NNewsDBReader
from settings import (
    LOGGER,
    MESSAGE_SIZE_LIMIT,
    full_escape_markdown,
    escape_markdown,
)

# Imports from telegram framework python-telegram-bot
from telegram import (
    Update,
)
from telegram.ext import (
    ContextTypes,
)


logger = LOGGER


async def dbf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Cmd per avere la lista degli articoli (non solo titoli) relativi
    ad una sorgente passata in modo, anche parziale, come primo argomento
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
        messages = NNewsDBReader.dbfonte(defNum=5, defSearch=default)
        if not messages:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Mi dispiace ma non ho trovato nessuna fonte con la parola {default}",
                parse_mode="MarkdownV2",
            )
            return
        else:
            for message in messages:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=full_escape_markdown(message),
                        parse_mode="MarkdownV2",
                    )
                except Exception as e:
                    logger.error(
                        f"Non sono riuscito a mandare questo msg: {escape_markdown(message)}"
                    )
                    logger.error(e)
                    continue
        return
    except Exception as e:
        logger.error(e)
        await context.bot.send_message(
            chat_id=chat_id,
            text=full_escape_markdown(format(e)),
            parse_mode="MarkdownV2",
        )
    return


async def lus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    List User's source (ADMIN)
    """
    user = update.effective_user
    chat_id = user.id
    user_to_check = ""
    if len(context.args) == 1:
        user_to_check = context.args[0]
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione list user's sources senza passare utente",
            parse_mode="MarkdownV2",
        )
        return
    invio = ""
    try:
        messages = botutils.listUserSources(chat_id, str(user_to_check))
        for message in messages:
            invio = invio + message + "\n"
            if len(invio) > MESSAGE_SIZE_LIMIT:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=escape_markdown(invio),
                    parse_mode="MarkdownV2",
                )
                invio = ""
                return
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(invio), parse_mode="MarkdownV2"
        )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def bu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Ban user (ADMIN)
    """
    user = update.effective_user
    chat_id = user.id
    user_to_ban = ""
    if len(context.args) == 1:
        user_to_ban = context.args[0]
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione ban user senza passare l'utente da bannare",
            parse_mode="MarkdownV2",
        )
        return
    try:
        message = botutils.banuser(chat_id, str(user_to_ban))
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(message), parse_mode="MarkdownV2"
        )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def uu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Unban user (ADMIN)
    """
    user = update.effective_user
    chat_id = user.id
    user_to_unban = ""
    if len(context.args) == 1:
        user_to_unban = context.args[0]
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione unban user senza passare l'utente da sbannare",
            parse_mode="MarkdownV2",
        )
        return
    try:
        message = botutils.unbanuser(chat_id, str(user_to_unban))
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(message), parse_mode="MarkdownV2"
        )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def lut(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    List Users' topics (ADMIN)
    TODO: Controllare implementazione
    """
    user = update.effective_user
    chat_id = user.id
    user_to_check = ""
    if len(context.args) == 1:
        user_to_check = context.args[0]
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione list user's topics senza passare utente",
            parse_mode="MarkdownV2",
        )
        return
    invio = ""
    try:
        messages = botutils.listUserTopics(chat_id, str(user_to_check))
        for message in messages:
            invio = invio + message + "\n"
            if len(invio) > MESSAGE_SIZE_LIMIT:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=escape_markdown(invio),
                    parse_mode="MarkdownV2",
                )
                invio = ""
                return
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(invio), parse_mode="MarkdownV2"
        )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def ut(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    User topics (ADMIN)
    TODO: Controllare implementazione
    """
    user = update.effective_user
    chat_id = user.id
    user_to_check = topicList = ""
    if len(context.args) > 1:
        user_to_check = context.args[0]
        context.args.pop(0)
        if len(context.args) == 1:
            topicList = context.args[0]
        else:
            topicList = "|".join(context.args)
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione user topics senza passare gli argomenti necessari: utente e lista argomenti separati da spazio",
            parse_mode="MarkdownV2",
        )
        return
    try:
        message = botutils.updateTopicList(chat_id, str(user_to_check), topicList)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(message), parse_mode="MarkdownV2"
        )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def ac(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Add category (ADMIN)
    TODO: ricontrollare implementazione
    """
    category = ""
    user = update.effective_user
    chat_id = user.id
    if len(context.args) == 1:
        # Leggo il primo parametro
        category = context.args[0]
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione add category senza parametri o con un numero di parametri errato (ne basta uno)",
            parse_mode="MarkdownV2",
        )
        return
    try:
        message = botutils.insertCategory(chat_id, str(category))
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(message), parse_mode="MarkdownV2"
        )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def af(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Add feed (ADMIN)
    TODO: ricontrollare implementazione
    """
    category = feed = ""
    user = update.effective_user
    chat_id = user.id
    if len(context.args) > 0:
        if len(context.args) > 0:
            # Leggo il primo parametro
            category = context.args[0]
        if len(context.args) > 1:
            feed = context.args[1]
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Hai chiamato la funzione add feed senza i due parametri (category feed)",
            parse_mode="MarkdownV2",
        )
        return
    try:
        message = botutils.insertFeed(chat_id, str(category), str(feed))
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(message), parse_mode="MarkdownV2"
        )
    except ValueError as e:
        logger.error(e.message)
        await context.bot.send_message(
            chat_id=chat_id, text=escape_markdown(format(e)), parse_mode="MarkdownV2"
        )
    return


async def db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Visualizza gli ultimi X articoli inseriti nel db
    In sintesi, per verificare che il meccanismo di aggiornamento sta funzionando
    """
    chat_id = update.effective_user.id
    messages = NNewsDBReader.dbreader(defNum=5)
    for message in messages:
        await context.bot.send_message(
            chat_id=chat_id, text=full_escape_markdown(message), parse_mode="MarkdownV2"
        )
    return
