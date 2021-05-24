import dotenv
import os


dotenv.load_dotenv()

COLOUR_INFO = 0x09d03a
COLOUR_ERROR = 0xd31414
THUMBNAIL_URL = os.environ.get('THUMBNAIL_URL')
GITHUB_URL = "https://github.com/quanta-kt/CosmicDiversBot"
CREATOR_NAME = "अभि#8608"
PREFIX = os.environ.get("BOT_PREFIX") or "~"

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")
CRASH_WEBHOOK_ID = os.environ.get("CRASH_WEBHOOK_ID")
