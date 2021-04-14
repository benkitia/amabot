# The bot will not work if all of the integer values are not replaced.
# Making any edits outside of replacing values isn't reccomended and could break the bot.
# Make sure you rename this file config.py

import os

class Config:
    submission_channel_id = 123456789012345678 # The channel where participants ask questions
    queue_channel_id = 123456789012345678 # The channel where questions are approved/denied. Only moderators should have access to this channel.
    answering_channel_id = 123456789012345678 # The channel where the guest responds to questions in. This channel should only be visible to the guest and as little users as possible.
    ama_channel_id = 123456789012345678 # The channel where questions and answers are posted. Should be visible to the everyone and no one should be able to send messages.
    log_channel_id = 123456789012345678 # The channel where all actions are logged

    guest_name = "Trisha Paytas" # The guest's name
    guest_avatar_url = "https://i.imgur.com/Y7po41E.jpg" # An avatar URL for the guest
    guest_user_id = 123456789012345678 # The user ID for the guest
    color = 0x000000 # The accent color for embeds
    require_question_mark = True # Whether you want the bot to reject questions not ending in a "?". Don't forget the capital T or F
    guild_id = 123456789012345678 # The ID for the guild in which the AMA is being hosted
    prefix = "a!" # The desired charectar(s) preceeding a command