import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

DB_FILE = "database.json"

# Базовая БД (ID теперь всегда числа)
DEFAULT_DB = {
    "players": {
        1: {"id": 1, "username": "Knight_Vlad", "gold": 250}
    },
    "items": {
        101: {"id": 101, "name": "Sword of Kings", "price": 100},
        102: {"id": 102, "name": "Health Potion", "price": 30}
    },
    "inventories": [
        {"player_id": 1, "item_id": 102, "quantity": 2}
    ]
}

app = FastAPI(title="Game Shop API")


# Схема входящего запроса. FastAPI автоматически проверит типы данных!
class BuyRequest(BaseModel):
    player_id: int
    item_id: int


def load_db() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        save_db(DEFAULT_DB)
        return DEFAULT_DB
    
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Конвертируем строковые ключи JSON обратно в int
        data["players"] = {int(k): v for k, v in data["players"].items()}
        data["items"] = {int(k): v for k, v in data["items"].items()}
        return data


def save_db(data: Dict[str, Any]) -> None:
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@app.post("/api/v1/buy")
async def buy_item(request: BuyRequest):
    db = load_db()
    
    player = db["players"].get(request.player_id)
    item = db["items"].get(request.item_id)

    # Вместо возврата словарей с ошибками используем правильные HTTP-исключения
    if not player or not item:
        raise HTTPException(status_code=404, detail="Player or item not found")

    if player["gold"] < item["price"]:
        raise HTTPException(status_code=400, detail="Not enough gold for purchase!")

    # Списание золота
    player["gold"] -= item["price"]
    
    # Обновление инвентаря через встроенный цикл else
    for inv in db["inventories"]:
        if inv["player_id"] == request.player_id and inv["item_id"] == request.item_id:
            inv["quantity"] += 1
            break
    else:
        db["inventories"].append({
            "player_id": request.player_id, 
            "item_id": request.item_id, 
            "quantity": 1
        })

    save_db(db)

    return {
        "status": "success",
        "message": f"Successfully bought {item['name']}",
        "remaining_gold": player["gold"]
    }

if __name__ == '__main__':
    import uvicorn
    # Запуск локального сервера разработки
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
