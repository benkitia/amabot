import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import random
import Config

cluster = Config.CLUSTER
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
            response = response.replace(f"<@!{self.bot.user.id}>", "")
            question = response.partition('\n')[0]
            answer = response.replace(question, "")
            question = question.replace("> ", "", 1)
            question = question.replace("Question from ", "")
            question = question.replace("*", "")
            responsem = discord.Embed(
                description=f"**{question}** {answer}",
                color=Config.COLOR
            )
            responsem.set_author(
                icon_url=Config.GUEST_AVATAR_URL,
                name=Config.GUEST_NAME
            )
            public_facing_channel = self.bot.get_channel(
                Config.PUBLIC_FACING_CHANNEL_ID)
            await public_facing_channel.send(embed=responsem)
            await message.add_reaction('☑️')
        submission_channel = self.bot.get_channel(Config.SUMBISSION_CHANNEL_ID)
        if ctx.message.channel.id == submission_channel.id:
            if ctx.message.author.id == self.bot.user.id:
                return
            if ctx.message.content.startswith(Config.PREFIX):
                return
            if Config.REQUIRE_QUESTION_MARK:
                if not ctx.message.content.endswith("?"):
                    return await ctx.send(f"{ctx.message.author.mention} questions must end with a `?` else they won't be submitted")
            queue_channel = self.bot.get_channel(Config.QUEUE_CHANNEL_ID)
            question = ctx.message.content
            finddupe = questions.find_one({"question": question})
            if finddupe:
                return await ctx.send(f"{ctx.message.author.mention} Your question has been automatically denied: duplicate")
            questionid = random.randint(1000000000, 9999999999)
            find_duplicate_question_id = questions.find_one({"qid":str(questionid)})
            while find_duplicate_question_id:
                questionid = random.randint(1000000000, 9999999999)
            newquestion = {
                "user": str(ctx.message.author.id),
                "qid": str(questionid),
                "question": str(question),
                "status": "Pending",
                "mod": ""
            }
            questions.insert_one(newquestion)
            embed = discord.Embed(
                title=f"New question",
                description=question,
                color=Config.COLOR
            )
            embed.set_author(
                name=f"{ctx.message.author} ({ctx.message.author.id})",
                icon_url=ctx.message.author.avatar_url
            )
            embed.set_footer(text=f"Question ID: {questionid}")
            qpost = await queue_channel.send(questionid, embed=embed)
            await qpost.add_reaction('☑️')
            await qpost.add_reaction('❌')
            await ctx.send(f"{ctx.message.author.mention} Your question: `{question}` has been sent to moderators for approval. Thank you for participating! Question ID: {questionid}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.channel.id == Config.ANSWERING_CHANNEL_ID:
            if user.id == self.bot.user.id:
                return
            if str(reaction.emoji) == '❌':
                await reaction.message.delete()
                log_channel = self.bot.get_channel(Config.LOG_CHANNEL_ID)
                guestreject = discord.Embed(
                    title="Question Rejected by Guest",
                    description=reaction.message.content,
                    color=0xff563a
                )
                await log_channel.send(embed=guestreject)
        queue_channel = self.bot.get_channel(Config.QUEUE_CHANNEL_ID)
        if user.id == self.bot.user.id or reaction.message.channel.id != queue_channel.id:
            return
        try:
            questionid = int(reaction.message.content)
            questionid = str(questionid)
        except:
            return await reaction.message.channel.send("Non-question, can't approve that")
        log_channel = self.bot.get_channel(Config.LOG_CHANNEL_ID)
        result = questions.find_one({"qid": questionid})
        submitter = self.bot.get_user(int(result["user"]))
        question = result["question"]
        if str(reaction.emoji) == '☑️':
            try:
                questions.insert_one(({"_id": "1", "paused": "No"}))
            except:
                pass
            dynamicsettings = questions.find_one({"_id": "1"})
            paused = dynamicsettings["paused"]
            if paused == "Yes":
                return
            await reaction.message.delete()
            questions.update_one({"qid": questionid}, {
                                 "$set": {"status": "Approved"}})
            questions.update_one({"qid": questionid}, {
                                 "$set": {"mod": str(user.id)}})
            log = discord.Embed(
                title="Question Approved",
                description=f"Question #{questionid} from {submitter} ({submitter.id}): '`{question}`' approved by {user}",
                color=discord.Color.green()
            )
            submission_channel = self.bot.get_channel(
                Config.SUMBISSION_CHANNEL_ID)
            await submission_channel.send(f"{submitter.mention} Your question {questionid} was approved and may be answered shortly.")
            await log_channel.send(embed=log)
            answering_channel = self.bot.get_channel(
                Config.ANSWERING_CHANNEL_ID)
            questionpst = await answering_channel.send(f"**Question from {submitter.mention}:** {question}")
            await questionpst.add_reaction('❌')
        if str(reaction.emoji) == '❌':
            await reaction.message.delete()
            questions.update_one({"qid": questionid}, {
                                 "$set": {"status": "Denied"}})
            questions.update_one({"qid": questionid}, {
                                 "$set": {"mod": str(user.id)}})
            log = discord.Embed(
                title="Question Denied",
                description=f"Question #{questionid} from {submitter} ({submitter.id}) '`{question}`' denied by {user}",
                color=0xff563a
            )
            submission_channel = self.bot.get_channel(
                Config.SUMBISSION_CHANNEL_ID)
            await submission_channel.send(f"{submitter.mention} Your question {questionid} was denied by moderators.")
            await log_channel.send(embed=log)

    @commands.command()
    @commands.has_any_role(Config.STAFF_ROLE_ID, Config.ADMIN_ROLE_ID)
    async def question(self, ctx, questionid):
        try:
            questionid = int(questionid)
            questionid = str(questionid)
        except:
            return await ctx.send(":x: Invalid question ID: not a number")
        if len(questionid) != 10:
            return await ctx.send(":x: Invalid question ID: not 10 digits")
        try:
            result = questions.find_one({"qid": questionid})
            sid = int(result["user"])
            qid = result["qid"]
            question = result["question"]
            status = result["status"]
            mod = result["mod"]
        except:
            return await ctx.send(":x: Invalid question ID: question not found")
        submitter = self.bot.get_user(sid)
        mod = self.bot.get_user(int(mod))
        embed = discord.Embed(
            title=f"Question {qid}",
            description=f"""**Submitter:** {submitter} ({submitter.id})
            **Question:** {question}
            **Status:** {status}
            **Approved/denied by**: {mod}""",
            color=Config.COLOR
        )
        embed.set_footer(text=f"Requested by {ctx.message.author}")
        await ctx.send(embed=embed)

    @commands.command()
    async def stats(self, ctx):
        approved = questions.count_documents({"status": "Approved"})
        denied = questions.count_documents({"status": "Denied"})
        pending = questions.count_documents({"status": "Pending"})
        embed = discord.Embed(
            title="AMA Question Stats",
            description=f"""**Approved questions:** {approved}
            **Denied questions:** {denied}
            **Pending questions:** {pending}""",
            color=Config.COLOR
        )
        embed.set_footer(text=f"Requested by {ctx.message.author}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role(Config.STAFF_ROLE_ID, Config.ADMIN_ROLE_ID)
    async def ban(self, ctx, target: discord.Member = None, *, reason=None):
        if target == None:
            return await ctx.send(":x: You must provide a member to ban")
        if target.id == ctx.message.author.id:
            await ctx.send(":x: You can't ban yourself, silly")
        role = discord.utils.get(ctx.guild.roles, id=Config.BAN_ROLE_ID)
        await target.add_roles(role, reason=f"{ctx.message.author}: {reason}")
        await ctx.send(f":ok_hand: banned {target} from AMA channels (`{reason}`)")
        log_channel = self.bot.get_channel(Config.LOG_CHANNEL_ID)
        embed = discord.Embed(
            title="User AMA banned", description=f"{target} ({target.id}) banned by {ctx.message.author}\nReason: {reason}", color=0xff563a)
        await log_channel.send(embed=embed)

    @commands.command()
    @commands.has_any_role(Config.STAFF_ROLE_ID, Config.ADMIN_ROLE_ID)
    async def unban(self, ctx, target: discord.Member = None, *, reason=None):
        if target == None:
            return await ctx.send(":x: You must provide a member to unmute")
        if target.id == ctx.message.author.id:
            await ctx.send(":x: You can't unmute yourself, silly")
        role = discord.utils.get(ctx.guild.roles, id=Config.BAN_ROLE_ID)
        await target.remove_roles(role, reason=reason)
        await ctx.send(f":ok_hand: unmuted {target} (`{reason}`)")
        log_channel = self.bot.get_channel(Config.LOG_CHANNEL_ID)
        embed = discord.Embed(title="User AMA unbarred",
                              description=f"{target} ({target.id}) unmuted by {ctx.message.author}\nReason: {reason}", color=0x18ec6b)
        await log_channel.send(embed=embed)

    @commands.command()
    @commands.has_any_role(Config.STAFF_ROLE_ID, Config.ADMIN_ROLE_ID)
    async def approve(self, ctx, questionid):
        try:
            dynamicsettings = questions.find_one({"_id": "1"})
        except:
            questions.insert_one(({"_id": "1", "paused": "No"}))
            dynamicsettings = questions.find_one({"_id": "1"})
        paused = dynamicsettings["paused"]
        if paused == "Yes":
            return await (f"{ctx.message.author.mention} Can't approve, approving has been paused by an admin")
        try:
            questionid = int(questionid)
            questionid = str(questionid)
        except:
            return await ctx.send(":x: Invalid question ID: not a number")
        try:
            result = questions.find_one({"qid": questionid})
        except:
            return await ctx.send(":x: Invalid question ID: question not found")
        log_channel = self.bot.get_channel(Config.LOG_CHANNEL_ID)
        sidstr = result["user"]
        sid = int(sidstr)
        submitter = self.bot.get_user(sid)
        question = result["question"]
        questions.update_one({"qid": questionid}, {
                             "$set": {"status": "Approved"}})
        questions.update_one({"qid": questionid}, {
                             "$set": {"mod": str(ctx.message.author.name)}})
        log = discord.Embed(
            title="Question Approved",
            description=f"Question #{questionid} from {submitter} ({submitter.id}): '`{question}`' approved by {ctx.message.author.name}",
            color=0x18ec6b
        )
        submission_channel_id = Config.SUMBISSION_CHANNEL_ID
        submission_channel = self.bot.get_channel(submission_channel_id)
        await submission_channel.send(f"{submitter.mention} Your question {questionid} was approved and may be answered shortly.")
        await log_channel.send(embed=log)
        answering_channel = self.bot.get_channel(Config.ANSWERING_CHANNEL_ID)
        await answering_channel.send(f"**Question from {submitter.mention}:** {question}")

    @commands.command()
    @commands.has_role(Config.ADMIN_ROLE_ID)
    async def pause(self, ctx):
        questions.update_one({"_id": "1"}, {"$set": {"paused": "Yes"}})
        await ctx.send(":ok_hand: Paused")

    @commands.command()
    @commands.has_role(Config.ADMIN_ROLE_ID)
    async def unpause(self, ctx):
        questions.update_one({"_id": "1"}, {"$set": {"paused": "No"}})
        await ctx.send(":ok_hand: Unpaused")


def setup(bot):
    bot.add_cog(AMA(bot))
