# AMA Bot

AMA Bot is an open-source Discord bot for hosting crowd-sourced interviews right inside a Discord server.  

AMA Bot has been used to host guests like Rene Ritchie and Tailosive Tech, with hundreds of thousands of internet followers.

There is no publicly available instance being hosted, but it's fairly easy to set up the bot for use in your server.

## Hosting your own instance

### Prerequisites

- [Python](https://www.python.org/downloads/) version 3.9 or higher
- A [MongoDB](https://www.mongodb.com/) account and cluster (this is free)
- A Discord [application and bot account](https://discord.com/developers/applications/me) (also free)
- [Git](https://git-scm.com/downloads)

### Installing

1. Clone the repository: `git clone https://github.com/wwwaffles/amabot.git`
2. Login with your Discord account [here](https://discord.com/developers/applications) and click "New Application"
3. Click "Bot", then "Add Bot", then "Yes, do it"
4. Name your bot and add a profile picture (optional)
5. Copy and save your token somewhere safe
6. Create a MongoDB cluster, this should be easy to figure out. Give a database user access to the amabot collection and grab a URI for that user. Use Google as a resource if you're having difficulties
7. Create a collection called "amabot"
8. Rename config_example.py to config.py and replace the variables as described in the file
9. Rename .env.example to .env and paste in your Discord bot token and Mongo URI
10. Navigate to the main bot folder in terminal and run `pipenv install`
11. Run `pipenv run python3 main.py`

## Using The Bot

When a user posts a question (with a question mark) in the specified submission channel it'll be sent to the queue channel. When a mod approves the question with a reaction it'll be sent to the ama channel where the guest can answer the question by replying to the message using Discord's built-in replies  

The queue channel should only be viewable by mods and the guest answer channel should only be viewable by mods and the guest.  

Run the help command to get a list of commands, they're all self-explanatory.  

## Contributing

I encourage community contributions! I'll merge any helpful pull requests  

Use [this](http://www.contribution-guide.org/) as a guide  
