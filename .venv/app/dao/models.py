from datetime import datetime
from sqlalchemy import BigInteger, String
from app.dao.database import Base
from sqlalchemy import Integer, Date, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None]
    phone_nom: Mapped[str | None]
    description: Mapped[str | None]
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="user")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url_photo: Mapped[str]
    description: Mapped[str | None]
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="room")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id"))
    date_start: Mapped[datetime] = mapped_column(Date)
    date_end: Mapped[datetime] = mapped_column(Date)
    status: Mapped[str]
    cost: Mapped[int]
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    room: Mapped["Room"] = relationship("Room", back_populates="bookings")
    pays: Mapped[list["Pay"]] = relationship("Pay", back_populates="booking")

class Pay(Base):
    __tablename__ = "pays"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    summ: Mapped[int]
    id_booking: Mapped[int] = mapped_column(BigInteger, ForeignKey("bookings.id"))
    booking: Mapped["Booking"] = relationship("Booking", back_populates="pays")