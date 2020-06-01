import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import random

cluster = MongoClient("")
db = cluster["amabot"]
questions = db["questions"]
config = db["config"]

class AMA(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message):
        ctx: commands.Context = await self.bot.get_context(message)
        configvars = config.find_one({"_id":"1"})
        guest_channel_id = int(configvars["guest channel"])
        guest_channel = self.bot.get_channel(guest_channel_id)
        guest_id = int(configvars["guest id"])
        guest = self.bot.get_user(guest_id)
        botid = configvars["bot id"]
        if ctx.message.channel.id == guest_channel.id:
            if message.author.id != guest.id:
                return
            if not ctx.message.content.startswith(">"):
                return
            response = ctx.message.content
            response = response.replace(f"<@{botid}","")       
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
                icon_url=configvars["guest avatar url"],
                name=configvars["guest name"]
                )
            public_channel_id = int(configvars["public facing"])
            public_channel = self.bot.get_channel(public_channel_id)
            await public_channel.send(embed=responsem)
            await message.add_reaction('<:success:696628918043541585>')
        submission_channel_id = int(configvars["submit"])
        submission_channel = self.bot.get_channel(submission_channel_id)
        if ctx.message.channel.id == submission_channel.id:
            if not ctx.message.content.endswith("?"):
                configvars = config.find_one({"_id":"1"})
                botid = int(configvars["bot id"])
                if ctx.message.content.startswith("a!"):
                    return
                if ctx.message.author.id == botid:
                    return
                return await ctx.send(f"{ctx.message.author.mention} questions must end with a `?` else they won't be submitted")
            if ctx.message.content.endswith("?"):
                queue_id = int(configvars["queue"])
                queue = self.bot.get_channel(queue_id)
                question = ctx.message.content
                finddupe = questions.find_one({"content":question})
                if finddupe:
                    return await ctx.send(f"{ctx.message.author.mention} Your question has been automatically denied: duplicate")
                questionid = random.randint(10000, 99999)
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
                qpost = await queue.send(questionid, embed = embed)
                await qpost.add_reaction('<:Approve:710603870992203868>')
                await qpost.add_reaction('<:Deny:710603871130484776>')
                await ctx.send(f"{ctx.message.author.mention} Your question: `{question}` has been sent to mods for approval. Thank you for participating! You'll be able to ask another question in 5 minutes. Question ID: {questionid}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        configvars = config.find_one({"_id":"1"})
        queue_id = int(configvars["queue"])
        queue = self.bot.get_channel(queue_id)
        if user.id == self.bot.user.id or reaction.message.channel.id != queue.id:
            return
        try:
            questionid = int(reaction.message.content)
            questionid = str(questionid)
        except:
            return await reaction.message.channel.send("Non-message, can't approve that")
        logchannel_id = int(configvars["log"])
        logchannel = self.bot.get_channel(logchannel_id)
        result = questions.find_one({"qid":questionid})
        sidstr = result["uid"]
        sid = int(sidstr)
        submitter = self.bot.get_user(sid)
        question = result["content"]
        if str(reaction.emoji) == '<:Approve:710603870992203868>':
            result1 = config.find_one({"_id":"1"})
            paused = result1["paused"]
            if paused == "Yes":
                return
                # return await ctx.send(f"{user.mention} Can't approve, approving has been paused by an admin")
            await reaction.message.delete()
            questions.update_one({"qid":questionid},{"$set":{"status":"Approved"}})
            questions.update_one({"qid":questionid},{"$set":{"mod":str(user.name)}})
            log = discord.Embed(
                title="Question Approved",
                description=f"Question #{questionid} from {submitter} ({submitter.id}): '`{question}`' approved by {user.name}",
                color=0x3affa7
                )
            submission_channel_id = int(configvars["submit"])
            submission_channel = self.bot.get_channel(submission_channel_id)
            await submission_channel.send(f"{submitter.mention} Your question {questionid} was approved and may be answered shortly.")
            await logchannel.send(embed=log)
            answer_channel_id = int(configvars["guest channel"])
            answer_channel = self.bot.get_channel(answer_channel_id)
            await answer_channel.send(f"**Question from {submitter.mention}:** {question}")
        if str(reaction.emoji) == '<:Deny:710603871130484776>':
            await reaction.message.delete()
            questions.update_one({"qid":questionid},{"$set":{"status":"Denied"}})
            questions.update_one({"qid":questionid},{"$set":{"mod":str(user.name)}})
            log = discord.Embed(
                title="Question Denied",
                description=f"Question #{questionid} from {submitter} ({submitter.id}) '`{question}`' denied by {user.name}",
                color=0xff7373
                )
            submission_channel_id = int(configvars["submit"])
            submission_channel = self.bot.get_channel(submission_channel_id)
            await submission_channel.send(f"{submitter.mention} Your question {questionid} was denied by moderators.")
            await logchannel.send(embed=log)

    @commands.command()
    @commands.has_role('Staff')
    async def question(self, ctx, questionidinput):
        try:
            questionid = int(questionidinput)
            questionid = str(questionid)
        except:
            return await ctx.send("<:Deny:710603871130484776> Invalid question ID: not a number")
        if len(questionid) != 5:
            return await ctx.send("<:Deny:710603871130484776> Invalid question ID: not 5 digits")
        try:
            result = questions.find_one({"qid":questionid})
            sid = int(result["uid"])
            qid = result["qid"]
            question = result["content"]
            status = result["status"]
            mod = result["mod"]
        except:
            return await ctx.send("<:Deny:710603871130484776> Invalid question ID: question not found")
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
    @commands.has_role('Staff')
    async def ban(self, ctx, target:discord.Member=None, *, reason=None):
        configvars = config.find_one({"_id":"1"})
        if target == None:
            return await ctx.send("<:Deny:710603871130484776> You must provide a member to mute")
        if target.id == ctx.message.author.id:
            await ctx.send("<:Deny:710603871130484776> You can't mute yourself, silly")
        role_id = int(configvars["ban role"])
        role = discord.utils.get(ctx.guild.roles, id=role_id)
        await target.add_roles(role, reason=f"{ctx.message.author}: {reason}")
        await ctx.send(f"<:Approve:710603870992203868> muted {target} from AMA channels (`{reason}`)")
        logchannel_id = int(configvars["log"])
        logchannel = self.bot.get_channel(logchannel_id)
        embed = discord.Embed(title="User AMA barred",description=f"{target} ({target.id}) muted by {ctx.message.author}\nReason: {reason}",color=0xEE7662)
        await logchannel.send(embed=embed)

    @commands.command()
    @commands.has_role('Staff')
    async def unban(self, ctx, target:discord.Member=None, *, reason=None):
        configvars = config.find_one({"_id":"1"})
        if target == None:
            return await ctx.send("<:Deny:710603871130484776> You must provide a member to unmute")
        if target.id == ctx.message.author.id:
            await ctx.send("<:Deny:710603871130484776> You can't unmute yourself, silly")
        role_id = int(configvars["ban role"])
        role = discord.utils.get(ctx.guild.roles, id=role_id)
        await target.remove_roles(role, reason=reason)
        await ctx.send(f"<:Approve:710603870992203868> unmuted {target} (`{reason}`)")
        logchannel_id = int(configvars["log"])
        logchannel = self.bot.get_channel(logchannel_id)
        embed = discord.Embed(title="User AMA unbarred",description=f"{target} ({target.id}) unmuted by {ctx.message.author}\nReason: {reason}",color=0xEE7662)
        await logchannel.send(embed=embed)

    @commands.command()
    @commands.has_role('Staff')
    async def approve(self, ctx, questionid):
        configvars = config.find_one({"_id":"1"})
        paused = configvars["paused"]
        if paused == "Yes":
            return await (f"{ctx.message.author.mention} Can't approve, approving has been paused by an admin")
        try:
            questionid = int(questionid)
            questionid = str(questionid)
        except:
            return await ctx.send("<:Deny:710603871130484776> Invalid question ID: not a number")
        if len(questionid) != 5:
            return await ctx.send("<:Deny:710603871130484776> Invalid question ID: not 5 digits")
        try:
            result = questions.find_one({"qid":questionid})
        except:
            return await ctx.send("<:Deny:710603871130484776> Invalid question ID: question not found")
        logchannel_id = int(configvars["log"])
        logchannel = self.bot.get_channel(logchannel_id)
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
        submission_channel_id = int(configvars["submit"])
        submission_channel = self.bot.get_channel(submission_channel_id)
        await submission_channel.send(f"{submitter.mention} Your question {questionid} was approved and may be answered shortly.")
        await logchannel.send(embed=log)
        answer_channel_id = int(configvars["guest channel"])
        answer_channel = self.bot.get_channel(answer_channel_id)
        await answer_channel.send(f"**Question from {submitter.mention}:** {question}")

    @commands.command()
    @commands.has_role('Administrator')
    async def pause(self, ctx):
        config.update_one({"_id":"1"},{"$set":{"paused":"Yes"}})
        await ctx.send(":ok_hand: Paused")

    @commands.command()
    @commands.has_role('Administrator')
    async def unpause(self, ctx):
        config.update_one({"_id":"1"},{"$set":{"paused":"No"}})
        await ctx.send(":ok_hand: Unpaused")

def setup(bot):
    bot.add_cog(AMA(bot))