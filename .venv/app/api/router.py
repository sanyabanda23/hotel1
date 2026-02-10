from datetime import datetime, timedelta
from faststream.rabbit.fastapi import RabbitRouter
from loguru import logger
from app.bot.create_bot import bot
from app.config import settings, scheduler
from app.dao.dao import BookingDAO
from app.dao.database import async_session_maker

async def disable_booking():
    async with async_session_maker() as session:
        await BookingDAO(session).complete_past_bookings()

async def send_admin_msg():
    async with async_session_maker() as session:
        await BookingDAO(session).complete_past_bookings()
        await bot.send_message(user_id, text=text)

