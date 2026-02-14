import locale
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from loguru import logger
from app.bot.booking.dialog import booking_dialog
from app.bot.my_bookings.dialog import list_bookings_dialog
from app.bot.admin.router import router as admin_router
from app.config import settings
from app.dao.database_midlware import DatabaseMiddlewareWithoutCommit, DatabaseMiddlewareWithCommit

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = RedisStorage.from_url(
    'redis://127.0.0.1:6379/0',
    key_builder=DefaultKeyBuilder(with_destiny=True)
)
dp = Dispatcher(storage=storage)


async def set_commands():
    """Функция для генерации командного меню."""
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault()) # Устанавливает видимые пользователям команды бота


def set_russian_locale():
    """универсальная функция для смены локализации бота"""
    try:
        # Пробуем установить локаль для Windows
        locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')
    except locale.Error:
        try:
            # Пробуем установить локаль для Linux/macOS
            locale.setlocale(locale.LC_TIME, 'ru_RU.utf8')
        except locale.Error:
            # Игнорируем ошибку, если локаль не поддерживается
            pass

async def start_bot():
    set_russian_locale()
    setup_dialogs(dp)                                                     # настраивает внутренние обработчики и middleware
    dp.update.middleware.register(DatabaseMiddlewareWithoutCommit())
    dp.update.middleware.register(DatabaseMiddlewareWithCommit())
    await set_commands()
    dp.include_router(booking_dialog)
    dp.include_router(list_bookings_dialog)
    dp.include_router(admin_router)

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f'Я запущен🥳.')
        except:
            pass
    logger.info("Бот успешно запущен.")

# Функция, которая выполнится когда бот завершит свою работу
async def stop_bot():
    try:
        for admin_id in settings.ADMIN_IDS:
            await bot.send_message(admin_id, 'Бот остановлен. За что?😔')
    except:
        pass
    logger.error("Бот остановлен!")