from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.admin.kbs import main_admin_kb, admin_back_kb
from app.config import settings
from app.dao.dao import UserDAO, BookingDAO

router = Router()