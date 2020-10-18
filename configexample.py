import pymongo
from pymongo import MongoClient

CLUSTER = MongoClient("") # put your MongoDB URI within the quotes

TOKEN = '' # Your bot token goes within the quotes

PREFIX = 'a!' # The desired charectar(s) preceeding a command

SUMBISSION_CHANNEL_ID = 123456789012345678 # The channel ID for the channel where users post their questions

QUEUE_CHANNEL_ID = 123456789012345678 # The channel ID for the channel where questions wait to be approved/denied

ANSWERING_CHANNEL_ID = 123456789012345678 # The channel ID for the channel where the guest types answers to the questions

PUBLIC_FACING_CHANNEL_ID = 123456789012345678 # The channel ID for the channel where questions/answers are posted

LOG_CHANNEL_ID = 123456789012345678 # The channel ID for the channel where all actions are logged

GUEST_USER_ID = 123456789012345678 # The user ID of the guest

BAN_ROLE_ID = 123456789012345678 # The role ID of the ban role

GUEST_NAME = "Barack Obama" # The guest's name

GUEST_AVATAR_URL = "https://i.imgur.com/MWpzv8a.jpg" # an avatar url for the guest

STAFF_ROLE_ID = 123456789012345678  # The role ID of the staff/moderator role

ADMIN_ROLE_ID = 123456789012345678 # The role ID of the administrator/server manager role

COLOR = 0x000000 # The hex value for the color you'd like the bot to use for embeds. Enter it after "0x" WITHOUT #


# THE BOT WILL BREAK IF ALL OF THE INT VALUES ARE NOT REPLACED!
# MAKING MAJOR EDITS TO THIS FILE OUTSIDE OF THE DIRECTIONS IN DOCUMENTATION WILL CAUSE THE BOT TO BREAK
# MAKE SURE YOU RENAME THIS FILE Config.py