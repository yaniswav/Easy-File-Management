import discord
import datetime
import sqlite3
import typing
from discord.ext import commands


class Clock:  # Due to the size of this script, we will make a seperate class for it
    """The class for interfacing with reminders"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Our current closest endtime
        self.endtime: typing.Optional[datetime.datetime] = None
        # The id of our reminder in the database
        self.id: typing.Optional[int] = None
        # The task that is currently running
        self._task: typing.Optional[asyncio.Task] = None
        self.bot.loop.create_task(self.update())  # Telling our code to update

    async def get_closest_reminder(self) -> asyncpg.Record:
        """This is just finding the closest ending reminder"""
        return await self.bot.db.fetchrow(
            ...
        )  # i'll leave this to you, look into ORDER BY and LIMIT for sql

    async def create(self,
                     reminder: str,
                     channel_id: int,
                     message_id: int,
                     user_id: int,
                     endtime: datetime.datetime
                     ) -> int:
        """Creating a new reminder"""

        quary = """INSERT INTO reminders (channel_id, message_id, user_id, reminder, endtime) VALUES(
            $1, $2, $3, $4, $5
        ) RETURNING id"""

        id = await self.bot.db.fetchval(
            quary, channel_id, message_id, user_id, reminder, endtime
        )  # Our quary, inserting into the database and getting the id
        # if the timer ends sooner then the current scheduled one
        if (not self._task or self._task.done()) or endtime < self.endtime:
            if self._task and not self._task.done():  # if the task exists
                self._task.cancel()  # cancel it
            self._task = self.bot.loop.create_task(
                self.end_timer(
                        # call this with the arguments we need
                    )
                )
            self.endtime = endtime
            self.id = id
            return id  # just return the id we want

    async def update(self):
        """Gets the closest reminder and schedules it"""
        reminder = await self.get_closest_reminder()
        if not reminder:
            return
        if not self._task or self._task.done():  # if the task is done or no task exists we just create the task
            self._task = self.bot.loop.create_task(
                self.end_timer(
                    # call this with the arguments we need
                )
            )
            self.endtime = reminder["endtime"]  # store the endtime
            self.id = reminder["id"]  # store the id
            return

        # Otherwise, if the reminder ends sooner then the current closest endtime
        if reminder["endtime"] < self.endtime:
            self._task.cancel()  # cancel the task
            self._task = self.bot.loop.create_task(
                self.end_timer(
                    # call this with the arguments we need
                )
            )
            self.endtime = reminder["endtime"]  # store the endtime
            self.id = reminder["id"]  # store the id

    # async def end_timer(self, ...):
    #     await discord.utils.sleep_until(endtime)  # sleeping until the endtime

    #     # send your message here

    #     # remove from database
    #     await self.bot.db.execute("DELETE FROM reminders WHERE id = $1", id)

    #     self.bot.loop.create_task(self.update())  # re update

    def stop(self):
        self._task.cancel()


class Reminders(commands.Cog):  # our cog
    """The cog for creating reminders"""

    def __init__(self, bot):
        self.bot = bot
        self.clock = Clock(bot)  # create our timer stuff

    @commands.command()
    async def remind(
        self, ctx, when, reminder  # i'll leave it to you to make the time converters
    ):
    """Create a reminder"""
      id = await self.clock.create(
           ...
           )  # creating our reminder


async def setup(bot):
    await bot.add_cog(Reminders(bot))  # adding our cog
