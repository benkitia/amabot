# AMA Bot

AMA Bot is an open-source Discord bot for hosting crown-sourced interviews right in your Discord server.
The bot was originally made for the [r/iPhone Discord](https://iphonediscord.info) by [waffles](https://bensonkitia.me) written in python using the [discord.py](https://github.com/Rapptz/discord.py)
AMA Bot has been used to host guests like Rene Ritchie and Tailosive Tech, with hundreds of thousands of internet followers
There is no publicly available instance being hosted, but it's fairly easy to set up the bot for use in your own server

For support, join the [Waffle Development Discord Guild](https://discord.com/invite/zrBqN2v) or email support@waffledev.xyz

## Hosting your own instance

### Prerequisites

- [discord.py](https://github.com/)
- [pymongo](https://pypi.org/project/pymongo/)
- A [MongoDB](https://www.mongodb.com/) account and cluster (this is free)

### Guide

1. Clone the respository or download the source code with the big green button near the top of the repo
2. Login with your Discord account [here](https://discord.com/developers/applications) and click "New Application"
3. Click "Bot", then "Add Bot", then "Yes, do it"
4. Name your bot and add a profile picture (optional)
5. Open main.py in a text editor and add a token inside the quotes
6. Create a MongoDB cluster, this should be easy to figure out. Use Google as a resource if you're having difficulties
7. Create a database called "amabot" and 2 collections called "questions" and "config" respectively
8. Import from configexaple.json to the config collection and replace variables
9. Grab your Mongo URI to connect to your cluster and paste it in the quotes within the brackets accompanying "MongoClient" near the top of admin.py and ama.py

It's useful to know a bit of python and discord.py to make edits like staff and admin roles

For support, join the [Waffle Development Discord Guild](https://discord.com/invite/zrBqN2v) or email support@waffledev.xyz

## Using The Bot

You'll need to replace the variables in the config document on Mongo.

When a user posts a question (with a question mark) in the specified submission channel it'll be sent to the queue channel. When a mod approves the question with a reaction it'll be sent to a channel where the guest can answer the question by quoting it and typing a reply.

The queue channel should only be viewable by mods and the guest answer channel should only be viewable by mods and the guest

Run a!help to get a list of commands, they're all self-explanatory.

For support, join the [Waffle Development Discord Guild](https://discord.com/invite/zrBqN2v) or email support@waffledev.xyz

## Contributing

I encourage community contributions! I'll merge any helpful pull requests
Use [this](http://www.contribution-guide.org/) as a guide

Copyright © 2020 Waffle Development
