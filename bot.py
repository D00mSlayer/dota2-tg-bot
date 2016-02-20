import requests
import sys
import telebot
import time

# SETTING CHARACTER ENCODING TO UTF-8
reload(sys)
sys.setdefaultencoding("utf-8")


# TOKEN RECEIVED FROM @BotFather
TOKEN = "<YOUR-BOT-TOKEN>"
bot = telebot.TeleBot(TOKEN)

# TOKEN RECEIVED FROM DOTA2 DEV SITE
DOTA_2_DEV_KEY = "<YOUR-DOTA2-DEV-KEY>"

# DOTA2 WEB APIS
MATCH_HISTORY_API = "https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v001/?match_id={}&key={}"
HEROES_API = "https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?key={}&language=en_us"
ITEMS_API = "https://api.steampowered.com/IEconDOTA2_570/GetGameItems/V001/?key={}&language=en_us"
MATCH_DETAILS_API = "https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v001/?match_id={}&key={}"
PLAYER_DETAILS_API = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?steamids={}&key={}"
STEAM_PROFILE = 'http://steamcommunity.com/profiles/{}'

STEAM_32_TO_64 = 76561197960265728
PRIVATE_ACCOUNT = 76561202255233023

@bot.message_handler(commands=["dmatch"])
def send_dota2_match_details(message):
    message_split = message.text.strip().split()
    match_id = message_split[1]
    api_url = MATCH_DETAILS_API.format(match_id, DOTA_2_DEV_KEY)
    try:
        req = requests.get(api_url)
    except Exception as e:
        bot.send_message(message.chat.id, 'Oops, something went wrong. Try again in sometime or it must be a live / private game.')
        return
    data = req.json()
    reply = get_message(data)
    bot.send_message(message.chat.id, reply, parse_mode="Markdown", disable_web_page_preview=True)


def get_message(data):
    message = []
    result = data.get('result')
    if result.get('error'):
        return result.get('error')
    if len(result.get('players')) > 0:
    	duration = result.get('duration')
    	total_duration = time.strftime("%-H:%M", time.gmtime(duration))
        radiant_victory = result.get('radiant_victory')
        if not radiant_victory:
            message.append("`DIRE VICTORY` ")
        else:
            message.append("`RADIANT VICTORY` ")
        message.append("_({})_\n\n".format(total_duration))
        players = result.get('players')
        try:
            heroes_req = requests.get(HEROES_API.format(DOTA_2_DEV_KEY))
        except Exception as e:
            return None
        heroes_json = heroes_req.json().get('result').get('heroes')
        radiant_message = "*Radiant Team*\n"
        dire_message = "*Dire Team*\n"
        for player in players:
            for hero in heroes_json:
                if player.get('hero_id') == hero.get('id'):
                    game_hero = hero.get('localized_name')
                    break
                else:
                    game_hero = 'N/A'
            game_account = player.get('account_id')
            game_slot = player.get('player_slot')
            game_level = player.get('level')
            game_kills = player.get('kills')
            game_assists = player.get('assists')
            game_deaths = player.get('deaths')
            game_last_hits = player.get('last_hits')
            game_denies = player.get('denies')
            game_xpm = player.get('xp_per_min')
            game_gpm = player.get('gold_per_min')
            game_item_0 = player.get('item_0')
            game_item_1 = player.get('item_1')
            game_item_2 = player.get('item_2')
            game_item_3 = player.get('item_3')
            game_item_4 = player.get('item_4')
            game_item_5 = player.get('item_5')
            item_0 = 'N/A'
            item_1 = 'N/A'
            item_2 = 'N/A'
            item_3 = 'N/A'
            item_4 = 'N/A'
            item_5 = 'N/A'
            items_url = ITEMS_API.format(DOTA_2_DEV_KEY)
            item_request = requests.get(items_url)
            item_json = item_request.json()
            items = item_json.get('result').get('items')
            for item in items:
                if game_item_0 == item.get('id'):
                    item_0 = item.get('localized_name')
                if game_item_1 == item.get('id'):
                    item_1 = item.get('localized_name')
                if game_item_2 == item.get('id'):
                    item_2 = item.get('localized_name')
                if game_item_3 == item.get('id'):
                    item_3 = item.get('localized_name')
                if game_item_4 == item.get('id'):
                    item_4 = item.get('localized_name')
                if game_item_5 == item.get('id'):
                    item_5 = item.get('localized_name')
            steam_account_id = game_account + STEAM_32_TO_64
            if steam_account_id == PRIVATE_ACCOUNT:
                steam_account_url = None
            else:
                steam_account_url = STEAM_PROFILE.format(steam_account_id)
            player_details_url = PLAYER_DETAILS_API.format(steam_account_id, DOTA_2_DEV_KEY)
            response = requests.get(player_details_url)
            resp_json = response.json()
            if resp_json.get('response'):
                if resp_json.get('response').get('players'):
                    users = resp_json.get('response').get('players')
                    for user in users:
                        game_name = user.get('personaname')
                else:
                    game_name = 'Anonymous'
            if game_slot < 5:
                radiant_message += u'\u2022 [{}]({})'.format(game_name, steam_account_url)
                radiant_message += ' _({} - {})_\n'.format(game_hero, game_level)
                radiant_message += '*Items*: {} | {} | {} | {} | {} | {}\n'.format(
                    item_0,
                    item_1,
                    item_2,
                    item_3,
                    item_4,
                    item_5
                )
                radiant_message += '{}/{}/{}\n'.format(
                    game_last_hits,
                    game_deaths,
                    game_assists
                )
                radiant_message += '{} Last Hits, {} Denies\n'.format(
                    game_last_hits,
                    game_denies
                )
                radiant_message += '{} XPM | {} GPM\n'.format(
                    game_xpm,
                    game_gpm
                )
            else:
                dire_message += u'\u2022 [{}]({})'.format(game_name, steam_account_url)
                dire_message += ' _({} - {})_\n'.format(game_hero, game_level)
                dire_message += '*Items*: {} | {} | {} | {} | {} | {}\n'.format(
                    item_0,
                    item_1,
                    item_2,
                    item_3,
                    item_4,
                    item_5
                )
                dire_message += '{}/{}/{}\n'.format(
                    game_last_hits,
                    game_deaths,
                    game_assists
                )
                dire_message += '{} Last Hits, {} Denies\n'.format(
                    game_last_hits,
                    game_denies
                )
                dire_message += '{} XPM | {} GPM\n'.format(
                    game_xpm,
                    game_gpm
                )
    message.append(radiant_message + '\n\n' + dire_message)
    
    message = ''.join(message)
    return message

bot.polling(True)
