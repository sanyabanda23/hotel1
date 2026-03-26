import asyncio
from contextlib import asynccontextmanager
from app.bot.create_bot import dp, start_bot, bot, stop_bot
from app.config import settings, scheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram.types import Update
from fastapi import FastAPI, Request
from loguru import logger
from app.api.router import disable_booking, send_admin_msg, show_rooms
from app.api.calendar_pgn import generate_calendar_report

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Бот запущен...")
    await start_bot()
    scheduler.start()
    scheduler.add_job(
        disable_booking,
        trigger=CronTrigger(hour=8, minute=30),  # Каждый день в 08:30
        id='disable_booking_task',
        replace_existing=True
    )
    scheduler.add_job(
        send_admin_msg,
        trigger=CronTrigger(hour=8, minute=32),  # Каждый день в 08:32
        id='send_booking_task',
        replace_existing=True
    )
    
    logger.info("Запуск polling...")
    try:
        # Запускаем polling в фоновом режиме
        polling_task = asyncio.create_task(dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()))
        yield
    finally:
        logger.info("Остановка polling...")
        # Отменяем задачу polling
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass

    logger.info("Бот остановлен...")
    await stop_bot()
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)