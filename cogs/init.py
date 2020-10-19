import discord
from discord.ext import commands

class Init(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(description="Returns bot response time")
    async def init(self, ctx, mode, process):
        if mode == "send":
            if process == "signup":
                def check(m):
                    return m.author == ctx.message.author and m.channel == ctx.message.channel
                await ctx.send("channel?")
                channelid = await self.bot.wait_for('message', check=check)
                channelid = channelid.content
                channel = self.bot.get_channel(int(channelid))
                await ctx.send("guest name?")
                guestname = await self.bot.wait_for('message', check=check)
                guestname = guestname.content
                embed = discord.Embed(
                    description = f"""The AMA (Ask Me Anything) is a crowdsourced interview, which we call an Ask Me Anything. Today's guest is **{guestname}**!

The interviewee begins the process by posting a message, describing who they are and what they do. Then users across the server post questions in <#727246890311090207> to be approved my moderators before seen by the guest.

You can ask a question every 5 minutes for the entirety of the AMA""",
                    color = 0xee7662
                )
                embed.add_field(
                    name = "Question Guidelines",
                    value = """
- Keep questions at least somewhat relevant to the subject matter of the guest's content. Avoid questions about the guest's day or how they're doing
- Only questions will be approved. Disguising suggestions and compliments with a ? will not get them past the queue
- Questions must be in accordance with the server's rules, which can be found in <#663928913390731264>
- Purchase advice and technical support questions should be directed to appropriate server channels, not the AMA
- It's hard to define low-effort or low-quality questions, but most know it when they see it. Such questions will be denied
- Duplicate questions, or questions that have already been asked will be denied

***All questions must end with a `?`. Any questions without a `?` will be automatically denied.***""",
                    inline = False
                )
                embed.add_field(
                    name = "Interested in participating?",
                    value = "If you'd like to ask the guest questions, all you have to do is **react to this message**",
                    inline = False
                )
                embed.set_footer(text="Notice: Not all questions that are approved will be answered. Moderators reserve the right to deny questions per their discretion. We, the server moderators, are not employees of the guest nor are we affiliated with them. Some questions, including duplicate questions will be automatically denied.")
                embed.set_author(name="AMA Signup and Guidlines")
                await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Init(bot))