from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())

    gifts = relationship("Gift", back_populates="owner")
    reservations = relationship("Reservation", back_populates="user")


class Gift(Base):
    __tablename__ = "gifts"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(String)
    est_price = Column(String)
    image_url = Column(String)
    product_url = Column(String)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime)
    archived_at = Column(DateTime)

    # Relacje
    owner = relationship("User", back_populates="gifts")
    reservation = relationship("Reservation", uselist=False, back_populates="gift")


class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "friend_id"),)

    user = relationship("User", foreign_keys=[user_id])
    friend = relationship("User", foreign_keys=[friend_id])


class Reservation(Base):
    __tablename__ = "reservations"

    # gift_id jest jednocześnie PRIMARY KEY i FOREIGN KEY
    gift_id = Column(
        Integer,
        ForeignKey("gifts.id", ondelete="CASCADE"),
        primary_key=True
    )

    reserved_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    reserved_at = Column(DateTime, server_default=func.now())

    # relacje
    gift = relationship("Gift", back_populates="reservation")
    user = relationship("User", back_populates="reservations")
