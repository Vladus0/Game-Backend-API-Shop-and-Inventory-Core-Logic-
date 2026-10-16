import json
import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

DB_FILE = "database.json"

DEFAULT_DB = {
    "players": {
        "1": {"id": 1, "username": "Knight_Vlad", "gold": 250}
    },
    "items": {
        "101": {"id": 101, "name": "Sword of Kings", "price": 100},
        "102": {"id": 102, "name": "Health Potion", "price": 30}
    },
    "inventories": [
        {"player_id": 1, "item_id": 102, "quantity": 2}
    ]
}

# --- СЛОЙ ВАЛИДАЦИИ ДАННЫХ (Pydantic) ---
class BuyRequest(BaseModel):
    player_id: int = Field(..., description="ID игрока совершающего покупку", example=1)
    item_id: int = Field(..., description="ID покупаемого предмета", example=101)

class BuyResponse(BaseModel):
    status: str
    message: str
    remaining_gold: int

# --- СЛОЙ РАБОТЫ С ДАННЫМИ (Файловая БД) ---
def load_db() -> dict:
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_DB, f, indent=4)
        return DEFAULT_DB
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data: dict):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# --- ИНИЦИАЛИЗАЦИЯ СЕРВЕРА ---
app = FastAPI(
    title="Game Shop & Inventory API",
    description="Асинхронный бэкенд внутриигрового магазина по принципам Clean Architecture",
    version="1.0.0"
)

# --- ЭНДПОИНТЫ (API Routes) ---

@app.post(
    "/api/v1/shop/buy", 
    response_model=BuyResponse,
    status_code=status.HTTP_200_OK,
    summary="Покупка игрового предмета",
    description="Проверяет баланс игрока, списывает золото, добавляет предмет в инвентарь и атомарно сохраняет состояние."
)
async def buy_item(request: BuyRequest):
    # Загружаем актуальное состояние "БД"
    db = load_db()
    
    player_id_str = str(request.player_id)
    item_id_str = str(request.item_id)

    player = db["players"].get(player_id_str)
    item = db["items"].get(item_id_str)

    # Вместо возврата строк с ошибками — бросаем честные HTTP-исключения
    if not player or not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Player or item not found"
        )

    # Серверный Античит (Защита от читерства)
    if player["gold"] < item["price"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Not enough gold for purchase!"
        )

    # Проведение транзакции
    player["gold"] -= item["price"]
    
    # Обновление инвентаря
    updated = False
    for inv in db["inventories"]:
        if inv["player_id"] == request.player_id and inv["item_id"] == request.item_id:
            inv["quantity"] += 1
            updated = True
            break
            
    if not updated:
        db["inventories"].append({
            "player_id": request.player_id, 
            "item_id": request.item_id, 
            "quantity": 1
        })

    # Сохраняем состояние
    save_db(db)

    return BuyResponse(
        status="success",
        message=f"Successfully bought {item['name']}",
        remaining_gold=player["gold"]
    )

@app.get("/api/v1/healthcheck", summary="Проверка статуса сервера")
async def healthcheck():
    return {"status": "ok", "service": "game-backend"}

if __name__ == '__main__':
    import uvicorn
    # Запуск локального сервера разработки
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
