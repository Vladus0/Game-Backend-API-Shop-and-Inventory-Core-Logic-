import json
import os

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


def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_DB, f, indent=4)
        return DEFAULT_DB
    
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def process_buy_item_request(json_request_body: str) -> str:
    db = load_db()  
    
    try:
        request_data = json.loads(json_request_body)
        player_id = str(request_data.get("player_id"))
        item_id = str(request_data.get("item_id"))
    except Exception:
        return json.dumps({"status": "error", "detail": "Invalid JSON"}, indent=4)

    player = db["players"].get(player_id)
    item = db["items"].get(item_id)

    if not player or not item:
        return json.dumps({"status": "error", "detail": "Player or item not found"}, indent=4)

    if player["gold"] < item["price"]:
        return json.dumps({"status": "error", "detail": "Not enough gold for purchase!"}, indent=4)

    player["gold"] -= item["price"]
    
    
    updated = False
    for inv in db["inventories"]:
        if inv["player_id"] == int(player_id) and inv["item_id"] == int(item_id):
            inv["quantity"] += 1
            updated = True
            break
            
    if not updated:
        db["inventories"].append({"player_id": int(player_id), "item_id": int(item_id), "quantity": 1})

    save_db(db)

    return json.dumps({
        "status": "success",
        "message": f"Successfully bought {item['name']}",
        "remaining_gold": player["gold"]
    }, indent=4)


if __name__ == '__main__':
    print("=== СИМУЛЯЦИЯ С ХРАНЕНИЕМ В ФАЙЛЕ ===")
    
    mock_request = '{"player_id": 1, "item_id": 101}'
    response = process_buy_item_request(mock_request)
    print(response)
    
    db_after = load_db()
    print(f"\nТекущее золото в файле: {db_after['players']['1']['gold']}")