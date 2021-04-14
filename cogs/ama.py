import asyncio
import datetime
from datetime import datetime, date, time
import discord
from discord.ext import commands
import random
import string

class AMA(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.config = bot.config
		self.db = bot.db

	async def submit_question(self, ctx, submitter, content):
		# Checks if question is a duplicate
		dupe = await self.db.questions.find_one({"content" : content})
		if dupe:
			return await ctx.send(f"{submitter.mention} Your question has been automatically denied: this question has already been asked")
		# Generates random question ID
		letters = ''.join(random.choice(string.ascii_letters) for i in range(6)).upper()
		numbers = str(random.randint(100000, 999999))
		question_id = letters + numbers
		duplicate_question_id = await self.db.questions.find_one({"_id" : question_id})
		while duplicate_question_id:
			numbers = str(random.randint(100000, 999999))
			question_id = letters + numbers
		# Inserts question to database
		await self.db.questions.insert_one({
			"_id" : question_id,
			"submitter" : str(submitter.id),
			"content" : content,
			"status" : "pending"
		})
		# Sends question to queue
		queue_channel = discord.utils.get(ctx.guild.text_channels, id = self.config.queue_channel_id)
		submission_channel = discord.utils.get(ctx.guild.text_channels, id = self.config.submission_channel_id)
		embed = discord.Embed(
			title = f"New Question",
			description = content,
			color = self.config.color
		)
		embed.set_author(
			name = f"{str(submitter)} ({submitter.id})",
			icon_url = submitter.avatar_url
		)
		queue_post = await queue_channel.send(question_id, embed = embed)
		await queue_post.add_reaction('✅')
		await queue_post.add_reaction('❌')
		# Notifies submitter
		await submission_channel.send(f"{submitter.mention} Your question has been sent to moderators for approval. Thank you for participating! Question ID: {question_id}")

	@commands.Cog.listener()
	async def on_message(self, message):
		ctx: commands.Context = await self.bot.get_context(message)
		if ctx.message.guild.id != self.config.guild_id:
			return

		# Submissions
		if ctx.message.channel.id == self.config.submission_channel_id:
			# Ignores if message is a command
			if ctx.message.content.startswith(self.config.prefix):
				return
			if ctx.message.author.id == self.bot.user.id:
				return
			# Checks for question mark if required
			if self.config.require_question_mark and not ctx.message.content.endswith(
				"?"):
				return await ctx.send(f"{ctx.message.author.mention} questions must end with a question mark.")
			# Sends question to queue
			await self.submit_question(ctx, ctx.message.author, ctx.message.content)
		
		# Answer from guest
		if ctx.message.channel.id == self.config.answering_channel_id:
			if ctx.message.author.id != self.config.guest_user_id:
				return
			if not ctx.message.reference:
				return
			# Gets question from database
			else:
				referenced_message = await ctx.message.channel.fetch_message(ctx.message.reference.message_id)
				question_id = referenced_message.content
			answer = ctx.message.content
			question = await self.db.questions.find_one({"_id" : question_id})
			# Adds answer to question in database
			await self.db.questions.update_one(question, {"$set": {"answer" : answer}})
			# Sends to AMA channel
			question = await self.db.questions.find_one({"_id" : question_id})
			submitter = self.bot.get_user(int(question["submitter"]))
			content = question["content"]
			answer = question["answer"]
			embed = discord.Embed(
				description = f"Question from {submitter.mention}:\n> {content}\n\n{answer}",
				color = self.config.color
			)
			embed.set_author(
				name = self.config.guest_name,
				icon_url = self.config.guest_avatar_url
			)
			ama_channel = discord.utils.get(ctx.guild.text_channels, id = self.config.ama_channel_id)
			await ama_channel.send(embed = embed)

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		ctx: commands.Context = await self.bot.get_context(reaction.message)
		# Ignores if guild is wrong or if AMAbot added reaction
		if ctx.message.guild.id != self.config.guild_id:
			return
		if user.id == self.bot.user.id:
			return

		# Queue channel
		if reaction.message.channel.id == self.config.queue_channel_id:
			# If approved
			if str(reaction.emoji) == '✅':
				question_id = reaction.message.content
				# Updates database document
				try:
					await self.db.questions.update_one({"_id" : question_id}, {"$set" : {"status" : "denied", "mod" : str(user.id)}})
				except:
					return
				# Deletes from queue
				await reaction.message.delete()
				# Sends to guest to be answered
				question = await self.db.questions.find_one({"_id" : question_id})
				embed = discord.Embed(
					description = question["content"],
					color = self.config.color
				)
				submitter = self.bot.get_user(int(question["submitter"]))
				embed.set_author(
					name = str(submitter),
					icon_url = submitter.avatar_url
				)
				answering_channel = discord.utils.get(ctx.guild.text_channels, id = self.config.answering_channel_id)
				await answering_channel.send(question_id, embed = embed)
				# Notifies submitter
				submission_channel = discord.utils.get(ctx.guild.text_channels, id = self.config.submission_channel_id)
				await submission_channel.send(f"{submitter.mention} your question {question_id} was approved and may be answered shortly.")
			# If denied
			if str(reaction.emoji) == '❌':
				question_id = reaction.message.content
				# Updates database document
				try:
					await self.db.questions.update_one({"_id" : question_id}, {"$set" : {"status" : "denied", "mod" : str(user.id)}})
				except:
					return
				# Deletes from queue
				await reaction.message.delete()
				# Notifies submitter
				question = await self.db.questions.find_one({"_id" : question_id})
				submitter = self.bot.get_user(int(question["submitter"]))
				submission_channel = discord.utils.get(ctx.guild.text_channels, id = self.config.submission_channel_id)
				await submission_channel.send(f"{submitter.mention} your question {question_id} was denied by moderators.")


def setup(bot):
	bot.add_cog(AMA(bot))