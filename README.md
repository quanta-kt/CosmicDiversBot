# CosmicDiversBot
A Discord bot written for The Cosmic Divers Discord server

# Deploying
Clone the repository and cd into it
```
git clone https://github.com/quanta-kt/CosmicDiversBot
cd CosmicDiversBot
```
Create a .env file with following variables:
```
BOT_TOKEN=<your bot toke>
MONGO_URI=<MongoDB URI>
CRASH_WEBHOOK_ID=<Webhook ID to post crash reports>
THUMBNAIL_URL=<Image URL to use as thumbnail in embed created by help command>
```
Create and activate a virtual environment (Optional, recommended)
```
python -m venv venv
source venv/bin/activate
```
Install the requirements
```
pip install -r requirements.txt
```
Run the `cdbot` module:
```
python -m cdbot
```

# Contributing
Feel free to open an issue to suggest a change, addition of a command/feature or to report a bug.
If you would like to work on the issue yourself, create a pull request.

# License
This project is licensed under the MIT License, see the [License](License) file for details.
