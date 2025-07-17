import logging
import requests
import time
from aiogram import Bot, Dispatcher, executor, types

# Telegram Bot API Token 
API_TOKEN = '5068695480:AAGFjq07b11NkmxMOSRNCZBhCv5_gmiU4Bs'

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ESPN Cricinfo live matches API
MATCH_LIST_URL = "https://hs-consumer-api.espncricinfo.com/v1/pages/matches/current?lang=en&latest=true"
match_data = requests.get(MATCH_LIST_URL).json()

# Function to get batsman name for scoring events
def batsmen(data, c):
    bat = data['supportInfo']['liveSummary']['batsmen']
    name = bat[0]['player']['longName']

    if c.get('isFour'):
        score = "FOUR from " + str(name)
        time.sleep(15)
        return score

    if c.get('isSix'):
        score = "SIX from " + str(name)
        time.sleep(15)
        return score

# Function to get bowler and wicket info
def bowler(data, w):
    bowl = data['supportInfo']['liveSummary']['bowlers']
    name = bowl[0]['player']['longName']
    batsman_name = data['supportInfo']['liveSummary']['batsmen'][0]['player']['longName']
    wicket = f"{name} TOOK THE WICKET OF {batsman_name}"
    time.sleep(15)
    return wicket

# Filter out live matches and prepare display string
live_matches = [
    [match['scribeId'], match['series']['objectId'], match['series']['longName']]
    for match in match_data['matches']
    if match['status'] == "Live"
]

selected_live = ""
for i, live_match in enumerate(live_matches):
    selected_live += f"Live {i + 1} ->> {live_match[2]}\n"

# /start and /help command handler
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if not live_matches:
        await message.reply("NO LIVE MATCHES")
    else:
        await message.reply(selected_live)

# Handler for user match selection and live updates
@dp.message_handler()
async def handle_match_selection(message: types.Message):
    try:
        # Parse user input for match index
        selected_match = message.text.lower().replace("live", "").strip()
        user_input = int(selected_match)
        current_match = live_matches[user_input - 1]

        while True:
            # API endpoint for live match details
            MATCH_DETAIL_URL = (
                f"https://hs-consumer-api.espncricinfo.com/v1/pages/match/details?"
                f"&seriesId={current_match[1]}&matchId={current_match[0]}&latest=true"
            )
            data = requests.get(MATCH_DETAIL_URL).json()
            commentary = data['recentBallCommentary']['ballComments'][0]

            # Check for scoring event or wicket
            is_six_or_four = commentary.get('isFour') or commentary.get('isSix')
            is_wicket = commentary.get('isWicket')
            comment_items = commentary.get('commentTextItems')
            over = commentary.get('oversActual')
            title = commentary.get('title')
            total_runs = commentary.get('totalRuns')

            if is_six_or_four:
                batsman_info = batsmen(data, commentary)
                msg = f"Over : {over}\nTitle : {title}\nRuns : {batsman_info}"
                await bot.send_message(-644768316, msg)
                if comment_items:
                    commentary_text = "Commentary: " + comment_items[0]['html']
                    await bot.send_message(-644768316, commentary_text)
                time.sleep(20)

            elif is_wicket:
                wicket_info = bowler(data, commentary)
                msg = f"Over : {over}\nTitle : {title}\nWicket : {wicket_info}"
                await bot.send_message(-644768316, msg)
                if comment_items:
                    commentary_text = "Commentary: " + comment_items[0]['html']
                    await bot.send_message(-644768316, commentary_text)
                time.sleep(25)

            else:
                msg = f"Over : {over}\nTitle : {title}\nRuns : {total_runs}"
                await bot.send_message(-644768316, msg)
                if comment_items:
                    commentary_text = "Commentary: " + comment_items[0]['html']
                    await bot.send_message(-644768316, commentary_text)
                else:
                    await bot.send_message(-644768316, "----------No Commentary Available----------")
                time.sleep(18)

    except (ValueError, IndexError):
        await message.reply("Invalid selection. Please choose a valid match number.")
    except Exception as e:
        await message.reply("An error occurred: " + str(e))
        logging.exception("Error in match selection handler")

# Start the bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
