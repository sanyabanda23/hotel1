from contextlib import asynccontextmanager
from app.bot.create_bot import dp, start_bot, bot, stop_bot
from app.config import settings, scheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram.types import Update
from fastapi import FastAPI, Request
from loguru import logger
from app.api.router import disable_booking, send_admin_msg, show_rooms

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
    webhook_url = settings.hook_url
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )
    logger.success(f"Вебхук установлен: {webhook_url}")
    yield
    logger.info("Бот остановлен...")
    await stop_bot()
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request) -> None:
    logger.info("Получен запрос с вебхука.")
    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot, update)
        logger.info("Обновление успешно обработано.")
    except Exception as e:
        logger.error(f"Ошибка при обработке обновления с вебхука: {e}")