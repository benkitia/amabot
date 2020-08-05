import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import random
import Config

cluster = MongoClient("mongodb+srv://trying:noodleman@cluster0-zjpih.mongodb.net/amabot?retryWrites=true&w=majority") # Put the Mongo URI within these brackets
db = cluster["amabot"]
questions = db["questions"]

class AMA(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
     
    @commands.Cog.listener()
    async def on_message(self, message):
        ctx: commands.Context = await self.bot.get_context(message)
        if ctx.message.channel.id == int(Config.ANSWERING_CHANNEL_ID):
            if message.author.id != Config.GUEST_USER_ID:
                return
            if not ctx.message.content.startswith(">"):
                return
            response = ctx.message.content
            response = response.replace(f"<@!{self.bot.user.id}>","")       
            question = response.partition('\n')[0]
            answer = response.replace(question, "")
            question = question.replace("> ","",1)
            question = question.replace("Question from ", "")
            question = question.replace("*","")
            responsem = discord.Embed(
                description=f"**{question}** {answer}",
                color=0xEE7662
                )
            responsem.set_author(
                icon_url=Config.GUEST_AVATAR_URL,
                name=Config.GUEST_NAME
                )
            public_facing_channel = self.bot.get_channel(Config.PUBLIC_FACING_CHANNEL_ID)
            await public_facing_channel.send(embed=responsem)
            await message.add_reaction('<:success:696628918043541585>')
        submission_channel = self.bot.get_channel(Config.SUMBISSION_CHANNEL_ID)
        if ctx.message.channel.id == submission_channel.id:
            if not ctx.message.content.endswith("?"):
                if ctx.message.content.startswith("a!"):
                    return
                if ctx.message.author.id == self.bot.user.id:
                    return
                return await ctx.send(f"{ctx.message.author.mention} questions must end with a `?` else they won't be submitted")
            if ctx.message.content.endswith("?"):
                queue_channel = self.bot.get_channel(Config.QUEUE_CHANNEL_ID)
                question = ctx.message.content
                finddupe = questions.find_one({"content":question})
                if finddupe:
                    return await ctx.send(f"{ctx.message.author.mention} Your question has been automatically denied: duplicate")
                questionid = random.randint(1000000000, 9999999999)
                newquestion = {
                    "user":str(ctx.message.author),
                    "uid":str(ctx.message.author.id),
                    "qid":str(questionid),
                    "content":str(question),
                    "status":"Pending",
                    "mod":""
                    }
                questions.insert_one(newquestion)
                embed = discord.Embed(
                    title=f"New question",
                    description=question,
                    color=0xEE7662
                    )
                embed.set_author(
                    name=f"{ctx.message.author} ({ctx.message.author.id})",
                    icon_url=ctx.message.author.avatar_url
                    )
                embed.set_footer(text=f"Question ID: {questionid}")
                qpost = await queue_channel.send(questionid, embed = embed)
                await qpost.add_reaction(':ballot_box_with_check:')
                await qpost.add_reaction(':regional_indicator_x:')
                await ctx.send(f"{ctx.message.author.mention} Your question: `{question}` has been sent to mods for approval. Thank you for participating! You'll be able to ask another question in 5 minutes. Question ID: {questionid}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.channel.id == Config.ANSWERING_CHANNEL_ID:
            if user.id == self.bot.user.id:
                return
            if str(reaction.emoji) == ':regional_indicator_x:':
                await reaction.message.delete()
        queue_channel = self.bot.get_channel(Config.QUEUE_CHANNEL_ID)
        if user.id == self.bot.user.id or reaction.message.channel.id != queue_channel.id:
            return
        try:
            questionid = int(reaction.message.content)
            questionid = str(questionid)
        except:
            return await reaction.message.channel.send("Non-question, can't approve that")
        log_channel = self.bot.get_channel(Config.LOG_CHANNEL_ID)
        result = questions.find_one({"qid":questionid})
        sidstr = result["uid"]
        sid = int(sidstr)
        submitter = self.bot.get_user(sid)
        question = result["content"]
        if str(reaction.emoji) == ':ballot_box_with_check:':
            try:
                questions.insert_one(({"_id":"1","paused":"No"}))
            except:
                pass
            dynamicsettings = questions.find_one({"_id":"1"})
            paused = dynamicsettings["paused"]
            if paused == "Yes":
                return
            await reaction.message.delete()
            questions.update_one({"qid":questionid},{"$set":{"status":"Approved"}})
            questions.update_one({"qid":questionid},{"$set":{"mod":str(user.name)}})
            log = discord.Embed(
                title="Question Approved",
                description=f"Question #{questionid} from {submitter} ({submitter.id}): '`{question}`' approved by {user.name}",
                color=0x3affa7
                )
            submission_channel = self.bot.get_channel(Config.SUMBISSION_CHANNEL_ID)
            await submission_channel.send(f"{submitter.mention} Your question {questionid} was approved and may be answered shortly.")
            await log_channel.send(embed=log)
            answering_channel = self.bot.get_channel(Config.ANSWERING_CHANNEL_ID)
            questionpst = await answering_channel.send(f"**Question from {submitter.mention}:** {question}")
            await questionpst.add_reaction(':regional_indicator_x:')       
        if str(reaction.emoji) == ':regional_indicator_x:':
            await reaction.message.delete()
            questions.update_one({"qid":questionid},{"$set":{"status":"Denied"}})
            questions.update_one({"qid":questionid},{"$set":{"mod":str(user.name)}})
            log = discord.Embed(
                title="Question Denied",
                description=f"Question #{questionid} from {submitter} ({submitter.id}) '`{question}`' denied by {user.name}",
                color=0xff7373
                )
            submission_channel = self.bot.get_channel(Config.SUMBISSION_CHANNEL_ID)
            await submission_channel.send(f"{submitter.mention} Your question {questionid} was denied by moderators.")
            await log_channel.send(embed=log)

    @commands.command()
    @commands.has_role('Staff')
    async def question(self, ctx, questionidinput):
        try:
            questionid = int(questionidinput)
            questionid = str(questionid)
        except:
            return await ctx.send(":x: Invalid question ID: not a number")
        if len(questionid) != 10:
            return await ctx.send(":x: Invalid question ID: not 10 digits")
        try:
            result = questions.find_one({"qid":questionid})
            sid = int(result["uid"])
            qid = result["qid"]
            question = result["content"]
            status = result["status"]
            mod = result["mod"]
        except:
            return await ctx.send(":x: Invalid question ID: question not found")
        submitter = self.bot.get_user(sid)
        embed = discord.Embed(
            title=f"Question {qid}",
            description=f"""**Submitter:** {submitter} ({submitter.id})
            **Question:** {question}
            **Status:** {status}
            **Approved/denied by**: {mod}""",
            color=0xEE7662
            )
        embed.set_footer(text=f"Requested by {ctx.message.author}")
        await ctx.send(embed=embed)

    @commands.command()
    async def stats(self, ctx):
        approved = questions.count_documents({"status":"Approved"})
        denied = questions.count_documents({"status":"Denied"})
        pending = questions.count_documents({"status":"Pending"})
        embed = discord.Embed(
            title = "AMA Question Stats",
            description = f"""**Approved questions:** {approved}
            **Denied questions:** {denied}
            **Pending questions:** {pending}""",
            color=0xEE7662
        )
        embed.set_footer(text=f"Requested by {ctx.message.author}")
        await ctx.send(embed=embed)

    @commands.command()
    async def ban(self, ctx, target:discord.Member=None, *, reason=None):
        staffrole = discord.utils.get(ctx.guild.roles, id=Config.STAFF_ROLE_ID)
        if staffrole not in ctx.message.author.roles:
            await ctx.send(":x: You do not have permission to run this command")
        if target == None:
            return await ctx.send(":x: You must provide a member to mute")
        if target.id == ctx.message.author.id:
            await ctx.send(":x: You can't mute yourself, silly")
        role = discord.utils.get(ctx.guild.roles, id=Config.BAN_ROLE_ID)
        await target.add_roles(role, reason=f"{ctx.message.author}: {reason}")
        await ctx.send(f":ok_hand: muted {target} from AMA channels (`{reason}`)")
        log_channel_id = 727247203432792185
        log_channel = self.bot.get_channel(log_channel_id)
        embed = discord.Embed(title="User AMA barred",description=f"{target} ({target.id}) muted by {ctx.message.author}\nReason: {reason}",color=0xEE7662)
        await log_channel.send(embed=embed)

    @commands.command()
    async def unban(self, ctx, target:discord.Member=None, *, reason=None):
        staffrole = discord.utils.get(ctx.guild.roles, id=Config.STAFF_ROLE_ID)
        if staffrole not in ctx.message.author.roles:
            await ctx.send(":x: You do not have permission to run this command")
        if target == None:
            return await ctx.send(":x: You must provide a member to unmute")
        if target.id == ctx.message.author.id:
            await ctx.send(":x: You can't unmute yourself, silly")
        role = discord.utils.get(ctx.guild.roles, id=Config.BAN_ROLE_ID)
        await target.remove_roles(role, reason=reason)
        await ctx.send(f":ok_hand: unmuted {target} (`{reason}`)")
        log_channel_id = 727247203432792185
        log_channel = self.bot.get_channel(log_channel_id)
        embed = discord.Embed(title="User AMA unbarred",description=f"{target} ({target.id}) unmuted by {ctx.message.author}\nReason: {reason}",color=0xEE7662)
        await log_channel.send(embed=embed)

    @commands.command()
    async def approve(self, ctx, questionid):
        staffrole = discord.utils.get(ctx.guild.roles, id=Config.STAFF_ROLE_ID)
        if staffrole not in ctx.message.author.roles:
            await ctx.send(":x: You do not have permission to run this command")
        try:
            dynamicsettings = questions.find_one({"_id":"1"})
        except:
            questions.insert_one(({"_id":"1","paused":"No"}))
            dynamicsettings = questions.find_one({"_id":"1"})
        paused = dynamicsettings["paused"]
        if paused == "Yes":
            return await (f"{ctx.message.author.mention} Can't approve, approving has been paused by an admin")
        try:
            questionid = int(questionid)
            questionid = str(questionid)
        except:
            return await ctx.send(":x: Invalid question ID: not a number")
        try:
            result = questions.find_one({"qid":questionid})
        except:
            return await ctx.send(":x: Invalid question ID: question not found")
        log_channel = self.bot.get_channel(Config.LOG_CHANNEL_ID)
        sidstr = result["uid"]
        sid = int(sidstr)
        submitter = self.bot.get_user(sid)
        question = result["content"]
        questions.update_one({"qid":questionid},{"$set":{"status":"Approved"}})
        questions.update_one({"qid":questionid},{"$set":{"mod":str(ctx.message.author.name)}})
        log = discord.Embed(
            title="Question Approved",
            description=f"Question #{questionid} from {submitter} ({submitter.id}): '`{question}`' approved by {ctx.message.author.name}",
            color=0x3affa7
            )
        submission_channel_id = Config.SUMBISSION_CHANNEL_ID
        submission_channel = self.bot.get_channel(submission_channel_id)
        await submission_channel.send(f"{submitter.mention} Your question {questionid} was approved and may be answered shortly.")
        await log_channel.send(embed=log)
        answering_channel_id = config.ANSWERING_CHANNEL_ID
        answering_channel = self.bot.get_channel(Config.ANSWERING_CHANNEL_ID)
        await answering_channel.send(f"**Question from {submitter.mention}:** {question}")

    @commands.command()
    async def pause(self, ctx):
        adminrole = discord.utils.get(ctx.guild.roles, id=Config.ADMIN_ROLE_ID)
        if adminrole not in ctx.message.author.roles:
            await ctx.send(":x: You do not have permission to run this command")
        questions.update_one({"_id":"1"},{"$set":{"paused":"Yes"}})
        await ctx.send(":ok_hand: Paused")

    @commands.command()
    async def unpause(self, ctx):
        adminrole = discord.utils.get(ctx.guild.roles, id=Config.ADMIN_ROLE_ID)
        if adminrole not in ctx.message.author.roles:
            await ctx.send(":x: You do not have permission to run this command")
        questions.update_one({"_id":"1"},{"$set":{"paused":"No"}})
        await ctx.send(":ok_hand: Unpaused")

def setup(bot):
    bot.add_cog(AMA(bot))