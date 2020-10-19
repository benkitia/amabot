# AMA Bot

AMA Bot is an open-source Discord bot for hosting crown-sourced interviews right in your Discord server.  
The bot was originally made for the [r/iPhone Discord](https://iphonediscord.info) by [waffles](https://bensonkitia.me) written in python using the [discord.py](https://github.com/Rapptz/discord.py)  
AMA Bot has been used to host guests like Rene Ritchie and Tailosive Tech, with hundreds of thousands of internet followers  
There is no publicly available instance being hosted, but it's fairly easy to set up the bot for use in your own server

For support, join [my Discord Guild](https://discord.com/invite/zrBqN2v) or email support@bensonkitia.me

## Hosting your own instance

### Prerequisites

- [Python](https://www.python.org/downloads/) (3.8 or later reccomended)
- [pydsl](https://pypi.org/project/pydsl/)
- [discord.py](https://github.com/)
- [pymongo](https://pypi.org/project/pymongo/)
- A [MongoDB](https://www.mongodb.com/) account and cluster (this is free)
- A Discord [application and bot account](https://discord.com/developers/applications/me) (also free)

### Guide

1. Clone the respository or download the source code with the big green button near the top of the repo
2. Login with your Discord account [here](https://discord.com/developers/applications) and click "New Application"
3. Click "Bot", then "Add Bot", then "Yes, do it"
4. Name your bot and add a profile picture (optional)
5. Find and save your token somewhere safe
6. Create a MongoDB cluster, this should be easy to figure out. Use Google as a resource if you're having difficulties
7. Create a database called "amabot" with a collection called "questions"
8. Rename configexample.py to Config.py and replace the variables as described in the file
9. Navigate to the main bot folder in terminal and type `python main.py` if you're on Windows, and `python3 main.py` if you're on a unix-based OS (macOS or Linux)

For support, join [my Discord Guild](https://discord.com/invite/zrBqN2v) or email support@bensonkitia.me

## Using The Bot

When a user posts a question (with a question mark) in the specified submission channel it'll be sent to the queue channel. When a mod approves the question with a reaction it'll be sent to a channel where the guest can answer the question by quoting it and typing a reply.

The queue channel should only be viewable by mods and the guest answer channel should only be viewable by mods and the guest

If you're going to be utilizing the a!ban and a!unban commands, make sure that the role set under BAN_ROLE_ID in the config file does not have speaking access in the submission channel.

Run a!help to get a list of commands, they're all self-explanatory.

For support, join [my Discord Guild](https://discord.com/invite/zrBqN2v) or email support@bensonkitia.me

## Contributing

I encourage community contributions! I'll merge any helpful pull requests
Use [this](http://www.contribution-guide.org/) as a guide

Copyright © 2020 Benson Kitia
