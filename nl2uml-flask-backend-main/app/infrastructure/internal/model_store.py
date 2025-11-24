from __future__ import annotations
import json, os, sqlite3
from typing import Any, Dict, List, Optional

DATA_DIR_DEFAULT = "/var/lib/nl2uml"
JSON_FILENAME = "models.json"
SQLITE_DEFAULT = os.path.join(DATA_DIR_DEFAULT, "db", "nl2uml.sqlite")

class BaseModelStore:
    def get(self, model_id: str) -> Optional[Dict[str, Any]]: raise NotImplementedError
    def put(self, item: Dict[str, Any]) -> None: raise NotImplementedError
    def delete(self, model_id: str) -> None: raise NotImplementedError
    def list(self) -> List[Dict[str, Any]]: raise NotImplementedError

class SqliteModelStore(BaseModelStore):
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._ensure_schema()
    def _conn(self):
        cx = sqlite3.connect(self._db_path, check_same_thread=False, timeout=30.0)
        # Align SQLite tuning with other repos to reduce lock contention.
        cx.execute("PRAGMA journal_mode=WAL;")
        cx.execute("PRAGMA synchronous=NORMAL;")
        cx.execute("PRAGMA busy_timeout=30000;")
        return cx
    def _ensure_schema(self) -> None:
        with self._conn() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS models (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
            conn.commit()
    def get(self, model_id: str) -> Optional[Dict[str, Any]]:
        print(f"Retrieving model item with id: {model_id}")
        with self._conn() as conn:
            cur = conn.execute("SELECT payload FROM models WHERE id=?", (model_id,))
            row = cur.fetchone()
            return None if not row else json.loads(row[0])
    def put(self, item: Dict[str, Any]) -> None:
        print(f"Storing model item with id: {item.get('id')}")
        if not item or "id" not in item: raise ValueError("Model item must include an 'id' field.")
        payload = json.dumps(item)
        with self._conn() as conn:
            conn.execute("""INSERT INTO models (id,payload) VALUES (?,?)
                          ON CONFLICT(id) DO UPDATE SET payload=excluded.payload""", (item["id"], payload))
            conn.commit()
    def delete(self, model_id: str) -> None:
        print(f"Deleting model item with id: {model_id}")
        with self._conn() as conn:
            conn.execute("DELETE FROM models WHERE id=?", (model_id,)); conn.commit()
    def list(self) -> List[Dict[str, Any]]:
        print("Listing all model items")
        with self._conn() as conn:
            cur = conn.execute("SELECT payload FROM models")
            return [json.loads(row[0]) for row in cur.fetchall()]

class FileModelStore(BaseModelStore):
    def __init__(self, data_dir: Optional[str] = None) -> None:
        data_dir = data_dir or os.getenv("DATA_DIR", DATA_DIR_DEFAULT)
        os.makedirs(data_dir, exist_ok=True)
        self._path = os.path.join(data_dir, JSON_FILENAME)
        if not os.path.exists(self._path):
            with open(self._path, "w", encoding="utf-8") as f: json.dump({}, f)
    def _read(self) -> Dict[str, Dict[str, Any]]:
        with open(self._path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f); return data if isinstance(data, dict) else {}
            except Exception: return {}
    def _write(self, data: Dict[str, Dict[str, Any]]) -> None:
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f: json.dump(data, f)
        os.replace(tmp, self._path)
    def get(self, model_id: str) -> Optional[Dict[str, Any]]: return self._read().get(model_id)
    def put(self, item: Dict[str, Any]) -> None:
        if not item or "id" not in item: raise ValueError("Model item must include an 'id' field.")
        data = self._read(); data[item["id"]] = item; self._write(data)
    def delete(self, model_id: str) -> None:
        data = self._read(); 
        if model_id in data: del data[model_id]; self._write(data)
    def list(self) -> List[Dict[str, Dict[str, Any]]]:
        return list(self._read().values())

class DdbModelStore(BaseModelStore):
    def __init__(self, table_name: str, region: Optional[str] = None) -> None:
        import boto3
        if not table_name: raise RuntimeError("DynamoDB TABLE_NAME is required")
        region = region or os.getenv("AWS_REGION", "us-east-1")
        ddb = boto3.resource("dynamodb", region_name=region)
        self._table = ddb.Table(table_name)
    def get(self, model_id: str) -> Optional[Dict[str, Any]]:
        resp = self._table.get_item(Key={"id": model_id}); return resp.get("Item")
    def put(self, item: Dict[str, Any]) -> None:
        if not item or "id" not in item: raise ValueError("Model item must include an 'id' field.")
        self._table.put_item(Item=item)
    def delete(self, model_id: str) -> None: self._table.delete_item(Key={"id": model_id})
    def list(self) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []; scan_kwargs: Dict[str, Any] = {}
        while True:
            resp = self._table.scan(**scan_kwargs); items.extend(resp.get("Items", []))
            last = resp.get("LastEvaluatedKey"); 
            if not last: break
            scan_kwargs["ExclusiveStartKey"] = last
        return items

# def ModelStore() -> BaseModelStore:
#     sqlite_path = os.getenv("SQLITE_DB_PATH")
#     default_exists = os.path.exists(SQLITE_DEFAULT)
#     if sqlite_path or default_exists: return (sqlite_path or SQLITE_DEFAULT)
#     use_ddb = os.getenv("USE_DYNAMODB", "").lower() in ("1","true","yes","on")
#     table_name = os.getenv("TABLE_NAME")
#     if use_ddb or table_name:
#         try: return DdbModelStore(table_name=table_name or "", region=os.getenv("AWS_REGION"))
#         except Exception as e: print(f"[model_store] Falling back to file store: {e}")
#     return FileModelStore()

def ModelStore() -> BaseModelStore:
    """
    Priority:
      1) SQLite if SQLITE_DB_PATH is set or the default sqlite file exists.
      2) DynamoDB if USE_DYNAMODB=true or TABLE_NAME is set.
      3) Local JSON file fallback.
    """
    # 1) SQLite
    sqlite_path = os.getenv("SQLITE_DB_PATH")
    default_exists = os.path.exists(SQLITE_DEFAULT)
    if sqlite_path or default_exists:
        # 👇 instantiate the store (do NOT return the path string)
        return SqliteModelStore(sqlite_path or SQLITE_DEFAULT)

    # 2) DynamoDB
    use_ddb = os.getenv("USE_DYNAMODB", "").lower() in ("1", "true", "yes", "on")
    table_name = os.getenv("TABLE_NAME")
    if use_ddb or table_name:
        try:
            return DdbModelStore(table_name=table_name or "", region=os.getenv("AWS_REGION"))
        except Exception as e:
            print(f"[model_store] Falling back to file store: {e}")

    # 3) Local JSON fallback
    return FileModelStore()
