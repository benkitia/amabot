# IMPORTANT - PLEASE READ:
# The bot will not work if all of the integer values are not replaced.
# Don't change variable names unless you're going to be sure to replace their references throughout the code.
# Make sure you duplicate this file and rename the duplicate config.py

import os


class Config:
    # The channel where participants ask questions.
    submission_channel_id = 123456789012345678
    # The channel where questions are approved/denied. Only moderators should have access to this channel (at least read perms).
    queue_channel_id = 123456789012345678
    # The channel where the guest responds to questions in. Ideally, this channel should only be viewable by the guest and whoever's running the bot (as few people as possible).
    answering_channel_id = 123456789012345678
    # The channel where questions and answers are posted. Should be read-only to all participants.
    ama_channel_id = 123456789012345678

    guest_name = "Trisha Paytas"  # The guest's name
    # An avatar URL for the guest. Make sure it's a direct link to the image (ending in .jpg, .png, etc.)
    guest_avatar_url = "https://i.imgur.com/Y7po41E.jpg"
    guest_user_id = 123456789012345678  # The user ID for the guest
    color = 0x000000  # The accent color for embeds. Format like this: #FFFFFF -> 0xFFFFFF
    # Whether you want the bot to reject questions not ending in a "?". Can be "True" or "False" (with a capital "T" or "F").
    require_question_mark = True
    # The ID for the guild in which the AMA is being hosted
    guild_id = 123456789012345678
