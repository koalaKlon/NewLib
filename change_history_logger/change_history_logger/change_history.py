from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable
from functools import wraps
from pymongo import MongoClient

class ChangeLogger:
    def __init__(self, mongo_uri: str, db_name: str, collection_name: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection_name = collection_name

    def log_change_history(
        self,
        actor: str,
        action: str,
        action_type: str,
        timestamp: Optional[datetime] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a change history entry into MongoDB collection.
        """
        doc = {
            "actor": actor,
            "action": action,
            "action_type": action_type,
            "timestamp": timestamp or datetime.now(timezone.utc),
        }
        if payload is not None:
            doc["payload"] = payload

        self.db[self.collection_name].insert_one(doc)

    def log_change(self, action: str, action_type: str):
        """
        Decorator for auto logging around functions.
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)

                actor = kwargs.get("actor", "unknown")
                payload = kwargs.get("payload", None)
                timestamp = kwargs.get("timestamp", datetime.now(timezone.utc))

                if isinstance(result, dict):
                    actor = result.get("actor", actor)
                    payload = result.get("payload", payload)
                    timestamp = result.get("timestamp", timestamp)

                self.log_change_history(
                    actor=actor,
                    action=action,
                    action_type=action_type,
                    timestamp=timestamp,
                    payload=payload,
                )
                return result
            return wrapper
        return decorator
