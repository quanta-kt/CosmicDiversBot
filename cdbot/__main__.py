import argparse
from .bot import CDBot
from . import config


parser = argparse.ArgumentParser()
parser.add_argument("--debug", "-d", action="store_true")
args = parser.parse_args()

bot = CDBot(debug=args.debug)
bot.run(config.BOT_TOKEN)
