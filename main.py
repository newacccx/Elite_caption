import os
import re
import asyncio
from pyrogram import Client, filters, types, enums
from pyrogram.errors import FloodWait, MessageNotModified

# Fetch environment variables
app_id = os.getenv("app_id")
api_hash = os.getenv("api_hash")
bot_token = os.getenv("bot_token")
custom_caption = os.getenv("custom_caption", """Title 🎬: {file_name}
{series_info}Quality 💿 : {quality} {rip} x264
Audio 🔊: {language} {sub}

JOIN & SUPPORT | @HDCINEMA_1""")

# Ensure all environment variables are set
if not app_id or not api_hash or not bot_token:
    raise ValueError("⚠️ Missing one or more required environment variables: app_id, api_hash, bot_token")

AutoCaptionBot = Client(
    name="AutoCaptionBot",
    api_id=int(app_id),
    api_hash=api_hash,
    bot_token=bot_token
)

start_message = """
<b>👋Hello {}</b>
<b>I am an AutoCaption bot</b>
<b>All you have to do is add me to your channel and I will show you my power</b>
<b>@Mo_Tech_YT</b>"""

about_message = """
<b>• Name : [AutoCaption V1](t.me/{username})</b>
<b>• Developer : [Muhammed](https://github.com/PR0FESS0R-99)</b>
<b>• Language : Python3</b>
<b>• Library : Pyrogram v{version}</b>
<b>• Updates : <a href=https://t.me/Mo_Tech_YT>Click Here</a></b>
<b>• Source Code : <a href=https://github.com/PR0FESS0R-99/AutoCaption-Bot>Click Here</a></b>"""

@AutoCaptionBot.on_message(filters.private & filters.command(["start"]))
def start_command(bot: Client, update: types.Message):
    update.reply(start_message.format(update.from_user.mention),
                 reply_markup=start_buttons(bot),
                 parse_mode=enums.ParseMode.HTML,
                 disable_web_page_preview=True)

@AutoCaptionBot.on_callback_query(filters.regex("start"))
def start_callback(bot: Client, update: types.CallbackQuery):
    update.message.edit_text(start_message.format(update.from_user.mention),
                             reply_markup=start_buttons(bot),
                             parse_mode=enums.ParseMode.HTML,
                             disable_web_page_preview=True)

@AutoCaptionBot.on_callback_query(filters.regex("about"))
def about_callback(bot: Client, update: types.CallbackQuery):
    bot_info = bot.get_me()
    update.message.edit_text(about_message.format(version=Client.__version__, username=bot_info.username),
                             reply_markup=about_buttons(),
                             parse_mode=enums.ParseMode.HTML,
                             disable_web_page_preview=True)

@AutoCaptionBot.on_message(filters.channel)
async def edit_caption(bot: Client, update: types.Message):
    if custom_caption and update.caption:
        formatted_name = format_file_name(update.caption)
        season = extract_season(update.caption)
        episode = extract_episode(update.caption)
        languages = get_file_language(update.caption)
        quality = get_file_quality(update.caption)
        rip = get_file_rip(update.caption)
        subtitle = get_file_subtitle(update.caption)
        #audio = get_file_audio(update.caption)

        series_info = f"Series Info#️: {season}{episode}\n" if season else ""

        custom_caption_final = custom_caption.format(
            file_name=formatted_name, 
            language=languages, 
            season=season, 
            episode=episode, 
            quality=quality, 
            rip=rip, 
            sub=subtitle,
            series_info=series_info
        ).replace('\n\n', '\n').strip()

        try:
            await update.edit(custom_caption_final)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await update.edit(custom_caption_final)
        except MessageNotModified:
            pass

def format_file_name(caption: str) -> str:
    caption = caption.replace("_", " ")
    match_release_date = re.search(r'\b(19|20)\d{2}\b', caption)
    if match_release_date:
        release_date = match_release_date.group(0)
        name = caption.split(release_date)[0].strip()
        name = re.sub(r'\s*\([^)]*\)\s*', ' ', name).strip()
        return f"{name} ({release_date})"
    
    match_season = re.search(r'(S\d{2}|Season \d+)', caption, re.IGNORECASE)
    if match_season:
        season = match_season.group(1)
        name = caption.split(season)[0].strip()
        name = re.sub(r'\s*\([^)]*\)\s*', ' ', name).strip()
        return name
    
    name = re.sub(r'\s*\([^)]*\)\s*', ' ', caption).strip()
    return name

def extract_season(caption: str) -> str:
    match_season = re.search(r'(S\d{2}|Season \d+)', caption, re.IGNORECASE)
    if match_season:
        season = match_season.group(1)
        if season.lower().startswith('season'):
            season = f"S{int(season.split(' ')[-1]):02}"
        return season
    return ""

def extract_episode(caption: str) -> str:
    caption = caption.lower()
    if "complete" in caption or "combined" in caption:
        return "Complete"
    match_episode = re.search(r'(E\d+)(?:[-\s]*(?:E\d+|\d+))*', caption, re.IGNORECASE)
    if match_episode:
        episodes = match_episode.group(0)
        episodes = re.sub(r'\s+', '', episodes)
        if 'to' in episodes:
            episodes = re.sub(r'(\d+)\s*to\s*(\d+)', r'E\1-E\2', episodes)
        return episodes.upper()
    match_episode_word = re.search(r'episode\s*(\d+)', caption, re.IGNORECASE)
    if match_episode_word:
        episode_number = int(match_episode_word.group(1))
        return f"E{episode_number:02}"
    return ""

def get_file_language(caption: str) -> str:
    language_mapping = {
        'hindi': 'Hindi',
        'english': 'English',
        'spanish': 'Spanish',
        'french': 'French',
        'german': 'German',
        'chinese': 'Chinese',
        'japanese': 'Japanese',
        'korean': 'Korean',
        'russian': 'Russian',
        'arabic': 'Arabic',
        'marathi': 'Marathi',
        'malayalam': 'Malayalam', 
        'punjabi': 'Punjabi', 
        'telugu': 'Telugu',
        'tamil':'Tamil'
    }
    detected_languages = [f"#{language}" for keyword, language in language_mapping.items() if keyword.lower() in caption.lower()]
    return ' '.join(detected_languages) if detected_languages else 'Unknown'

def get_file_quality(caption: str) -> str:
    quality_keywords = ['480p', '720p', '1080p', '720pHEVC', '1080pHEVC']
    for quality in quality_keywords:
        if quality in caption:
            return quality
    return ""

def get_file_rip(caption: str) -> str:
    rip_keywords = ['HDRip', 'HDTC', 'WebRip', 'WEB-DL', 'HD-CAM', 'HDCAM', 'HDTVRip', 'HDTS']
    for rip in rip_keywords:
        if rip.lower() in caption.lower():
            return rip
    return ""

import os
import re
import asyncio
from pyrogram import Client, filters, types, enums
from pyrogram.errors import FloodWait, MessageNotModified

# Fetch environment variables
app_id = os.getenv("app_id")
api_hash = os.getenv("api_hash")
bot_token = os.getenv("bot_token")
custom_caption = os.getenv("custom_caption", """Title 🎬: {file_name}
{series_info}Quality 💿 : {quality} {rip} x264
Audio 🔊: {language} {sub}

JOIN & SUPPORT | @HDCINEMA_1""")

# Ensure all environment variables are set
if not app_id or not api_hash or not bot_token:
    raise ValueError("⚠️ Missing one or more required environment variables: app_id, api_hash, bot_token")

AutoCaptionBot = Client(
    name="AutoCaptionBot",
    api_id=int(app_id),
    api_hash=api_hash,
    bot_token=bot_token
)

start_message = """
<b>👋Hello {}</b>
<b>I am an AutoCaption bot</b>
<b>All you have to do is add me to your channel and I will show you my power</b>
<b>@Mo_Tech_YT</b>"""

about_message = """
<b>• Name : [AutoCaption V1](t.me/{username})</b>
<b>• Developer : [Muhammed](https://github.com/PR0FESS0R-99)</b>
<b>• Language : Python3</b>
<b>• Library : Pyrogram v{version}</b>
<b>• Updates : <a href=https://t.me/Mo_Tech_YT>Click Here</a></b>
<b>• Source Code : <a href=https://github.com/PR0FESS0R-99/AutoCaption-Bot>Click Here</a></b>"""

@AutoCaptionBot.on_message(filters.private & filters.command(["start"]))
def start_command(bot: Client, update: types.Message):
    update.reply(start_message.format(update.from_user.mention),
                 reply_markup=start_buttons(bot),
                 parse_mode=enums.ParseMode.HTML,
                 disable_web_page_preview=True)

@AutoCaptionBot.on_callback_query(filters.regex("start"))
def start_callback(bot: Client, update: types.CallbackQuery):
    update.message.edit_text(start_message.format(update.from_user.mention),
                             reply_markup=start_buttons(bot),
                             parse_mode=enums.ParseMode.HTML,
                             disable_web_page_preview=True)

@AutoCaptionBot.on_callback_query(filters.regex("about"))
def about_callback(bot: Client, update: types.CallbackQuery):
    bot_info = bot.get_me()
    update.message.edit_text(about_message.format(version=Client.__version__, username=bot_info.username),
                             reply_markup=about_buttons(),
                             parse_mode=enums.ParseMode.HTML,
                             disable_web_page_preview=True)

@AutoCaptionBot.on_message(filters.channel)
async def edit_caption(bot: Client, update: types.Message):
    if custom_caption and update.caption:
        formatted_name = format_file_name(update.caption)
        season = extract_season(update.caption)
        episode = extract_episode(update.caption)
        languages = get_file_language(update.caption)
        quality = get_file_quality(update.caption)
        rip = get_file_rip(update.caption)
        subtitle = get_file_subtitle(update.caption)

        series_info = f"Series Info#️: {season}{episode}\n" if season else ""

        custom_caption_final = custom_caption.format(
            file_name=formatted_name, 
            language=languages, 
            season=season, 
            episode=episode, 
            quality=quality, 
            rip=rip, 
            sub=subtitle,
            series_info=series_info
        ).replace('\n\n', '\n').strip()

        try:
            await update.edit(custom_caption_final)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await update.edit(custom_caption_final)
        except MessageNotModified:
            pass

def format_file_name(caption: str) -> str:
    caption = caption.replace("_", " ")
    match_release_date = re.search(r'\b(19|20)\d{2}\b', caption)
    
    if match_release_date:
        release_date = match_release_date.group(0)
        # Check if there is a bracket for release year
        if '(' + release_date + ')' in caption:
            name = caption.split('(' + release_date + ')')[0].strip()
        else:
            name = caption.split(release_date)[0].strip()
        name = re.sub(r'\s*\([^)]*\)\s*', ' ', name).strip()
        return f"{name} ({release_date})"
    
    match_season = re.search(r'(S\d{2}|Season \d+)', caption, re.IGNORECASE)
    if match_season:
        season = match_season.group(1)
        name = caption.split(season)[0].strip()
        name = re.sub(r'\s*\([^)]*\)\s*', ' ', name).strip()
        return name
    
    name = re.sub(r'\s*\([^)]*\)\s*', ' ', caption).strip()
    return name

def extract_season(caption: str) -> str:
    match_season = re.search(r'(S\d{2}|Season \d+)', caption, re.IGNORECASE)
    if match_season:
        season = match_season.group(1)
        if season.lower().startswith('season'):
            season = f"S{int(season.split(' ')[-1]):02}"
        return season
    return ""

def extract_episode(caption: str) -> str:
    caption = caption.lower()
    if "complete" in caption or "combined" in caption:
        return "Complete"
    match_episode = re.search(r'(E\d+)(?:[-\s]*(?:E\d+|\d+))*', caption, re.IGNORECASE)
    if match_episode:
        episodes = match_episode.group(0)
        episodes = re.sub(r'\s+', '', episodes)
        if 'to' in episodes:
            episodes = re.sub(r'(\d+)\s*to\s*(\d+)', r'E\1-E\2', episodes)
        return episodes.upper()
    match_episode_word = re.search(r'episode\s*(\d+)', caption, re.IGNORECASE)
    if match_episode_word:
        episode_number = int(match_episode_word.group(1))
        return f"E{episode_number:02}"
    return ""

def get_file_language(caption: str) -> str:
    language_mapping = {
        'hindi': 'Hindi',
        'english': 'English',
        'spanish': 'Spanish',
        'french': 'French',
        'german': 'German',
        'chinese': 'Chinese',
        'japanese': 'Japanese',
        'korean': 'Korean',
        'russian': 'Russian',
        'arabic': 'Arabic',
        'marathi': 'Marathi',
        'malayalam': 'Malayalam', 
        'punjabi': 'Punjabi', 
        'telugu': 'Telugu'
    }
    detected_languages = [f"#{language}" for keyword, language in language_mapping.items() if keyword.lower() in caption.lower()]
    return ' '.join(detected_languages) if detected_languages else 'Unknown'

def get_file_quality(caption: str) -> str:
    quality_keywords = ['480p', '720p', '1080p', '720pHEVC', '1080pHEVC']
    for quality in quality_keywords:
        if quality in caption:
            return quality
    return ""

def get_file_rip(caption: str) -> str:
    rip_keywords = ['HDRip', 'HDTC', 'WebRip', 'WEB-DL', 'HD-CAM', 'HDCAM', 'HDTVRip']
    for rip in rip_keywords:
        if rip.lower() in caption.lower():
            return rip
    return ""

def get_file_subtitle(caption: str) -> str:
    subtitle_keywords = ['Esub', 'Msub']
    for sub in subtitle_keywords:
        if sub.lower() in caption.lower():
            return f"({sub})"
    return ""

#def get_file_audio(caption: str) -> str:
    #audio_keywords = {'hqdub': 'HQDUB', 'cleaned': 'Cleaned', 'org': 'ORG'}
    #detected_audio = [audio_keywords[keyword] for keyword in audio_keywords if keyword.lower() in caption.lower()]
    #return ' '.join(detected_audio) if detected_audio else ""

def start_buttons(bot: Client) -> types.InlineKeyboardMarkup:
    bot_info = bot.get_me()
    buttons = [[
        types.InlineKeyboardButton("Updates", url="t.me/Mo_Tech_YT"),
        types.InlineKeyboardButton("About 🤠", callback_data="about")
    ], [
        types.InlineKeyboardButton("➕️ Add To Your Channel ➕️", url=f"http://t.me/{bot_info.username}?startchannel=true")
    ]]
    return types.InlineKeyboardMarkup(buttons)

def about_buttons() -> types.InlineKeyboardMarkup:
    buttons = [[
        types.InlineKeyboardButton("🏠 Back To Home 🏠", callback_data="start")
    ]]
    return types.InlineKeyboardMarkup(buttons)

print("Telegram AutoCaption V1 Bot Start")
print("Bot Created By https://github.com/PR0FESS")

AutoCaptionBot.run()
