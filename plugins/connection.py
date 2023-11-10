from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.connections_mdb import add_connection, all_connections, if_active, delete_connection
from info import ADMINS
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


@Client.on_message((filters.private | filters.group) & filters.command('connect'))
async def addconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"you Aᴅᴍɪɴ 🤣 Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        try:
            cmd, group_id = message.text.split(" ", 1)
        except:
            await message.reply_text(
                "<b>Enter in correct format!</b>\n\n"
                "<code>/connect groupid</code>\n\n"
                "<i>അതിനു ഞാൻ നിങ്ങളുടെ ഗ്രൂപ്പിൽ ഉണ്ടോ... 🤔!!  <code>/id</code></i>",
                quote=True
            )
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and userid not in ADMINS
        ):
            await message.reply_text("അതിനു ഞാൻ നിങ്ങളുടെ ഗ്രൂപ്പിൽ ഉണ്ടോ... 🤔!!", quote=True)
            return
    except Exception as e:
        logger.exception(e)
        await message.reply_text(
            "Invalid Group ID!\n\nIf correct, Nᴀ Uɴɢᴀ Gʀᴏᴜᴘ Lᴀ Eʀᴜᴋᴇɴ ɴᴀ • Cʜᴇᴄᴋ Pᴀɴɴᴜɴɢᴀ!!",
            quote=True,
        )

        return
    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == enums.ChatMemberStatus.ADMINISTRATOR:
            ttl = await client.get_chat(group_id)
            title = ttl.title

            addcon = await add_connection(str(group_id), str(userid))
            if addcon:
                await message.reply_text(
                    f"SᴜᴄᴄᴇssFᴜʟʟʏ Jᴏɪɴ Pᴀɴɴɪᴛᴇɴ Tᴏ **{title}**\nNow Mᴀɴᴀɢᴇ Uʀ Gʀᴏᴜᴘ Sᴇᴛᴛɪɴɢ Iɴ Mʏ Pᴍ!",
                    quote=True,
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                    await client.send_message(
                        userid,
                        f"Connected to **{title}** !",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
            else:
                await message.reply_text(
                    "am Aʟʀᴇᴀᴅʏ in it...🎉",
                    quote=True
                )
        else:
            await message.reply_text("അതിനു ഞാൻ നിങ്ങളുടെ ഗ്രൂപ്പിൽ ഉണ്ടോ... 🤔!!", quote=True)
    except Exception as e:
        logger.exception(e)
        await message.reply_text('something wrong try again', quote=True)
        return


@Client.on_message((filters.private | filters.group) & filters.command('disconnect'))
async def deleteconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Nᴇɴɢᴀ Aᴅᴅʀᴇss Iʟʟᴀ Tʜᴀ Aᴅᴍɪɴ Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text("Run /connections Tᴏ അതിനു ഞാൻ നിങ്ങളുടെ ഗ്രൂപ്പിൽ ഉണ്ടോ... 🤔!", quote=True)

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

        st = await client.get_chat_member(group_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            return

        delcon = await delete_connection(str(userid), str(group_id))
        if delcon:
            await message.reply_text("SᴜᴄᴄᴇssFᴜʟʟʏ Iɴᴛʜᴀ Gʀᴏᴜᴘ get out", quote=True)
        else:
            await message.reply_text("i didt Cᴏɴɴᴇᴄᴛ yet\nDo /connect to connect.", quote=True)


@Client.on_message(filters.private & filters.command(["connections"]))
async def connections(client, message):
    userid = message.from_user.id

    groupids = await all_connections(str(userid))
    if groupids is None:
        await message.reply_text(
            "അതിനു ഞാൻ നിങ്ങളുടെ ഗ്രൂപ്പിൽ ഉണ്ടോ... 🤔!!",
            quote=True
        )
        return
    buttons = []
    for groupid in groupids:
        try:
            ttl = await client.get_chat(int(groupid))
            title = ttl.title
            active = await if_active(str(userid), str(groupid))
            act = " - ACTIVE" if active else ""
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                    )
                ]
            )
        except:
            pass
    if buttons:
        await message.reply_text(
            "Uɴɢᴀ Gʀᴏᴜᴘ Dᴇᴛᴀɪʟs ;\n\n",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    else:
        await message.reply_text(
            "അതിനു ഞാൻ നിങ്ങളുടെ ഗ്രൂപ്പിൽ ഉണ്ടോ... 🤔!!",
            quote=True
        )
