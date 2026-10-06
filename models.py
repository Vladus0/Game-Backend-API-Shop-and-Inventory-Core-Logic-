# from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.orm import declarative_base

# Base = declarative_base()

# # Таблица игрока
# class PlayerModel(Base):
#     __tablename__ = "players"
    
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     gold = Column(Integer, default=100) # Даем 100 золота при регистрации

# # Таблица предметов
# class ItemModel(Base):
#     __tablename__ = "items"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True)
#     price = Column(Integer)

# # Таблица инвентаря
# class InventoryModel(Base):
#     __tablename__ = "inventories"
    
#     id = Column(Integer, primary_key=True, index=True)
#     player_id = Column(Integer, ForeignKey("players.id"))
#     item_id = Column(Integer, ForeignKey("items.id"))
#     quantity = Column(Integer, default=1)
