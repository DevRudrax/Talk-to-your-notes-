import logging
from typing import Optional, Dict, Any, List
from app.config import settings

logger = logging.getLogger("talk_to_your_notes.db")

_supabase_client = None
_supabase_admin_client = None


def get_supabase_client():
    global _supabase_client
    if _supabase_client is not None and not isinstance(_supabase_client, MockSupabaseClient):
        return _supabase_client

    if settings.SUPABASE_URL and not settings.SUPABASE_URL.startswith("https://mock"):
        try:
            from supabase import create_client
            key = settings.SUPABASE_PUBLISHABLE_KEY
            if key and (key.startswith("eyJ") or key.startswith("sb_publishable")):
                _supabase_client = create_client(
                    settings.SUPABASE_URL,
                    key
                )
                return _supabase_client
        except Exception as e:
            logger.warning(f"Could not connect to live Supabase client: {e}")

    _supabase_client = MockSupabaseClient()
    return _supabase_client


def get_supabase_admin_client():
    global _supabase_admin_client
    if _supabase_admin_client is not None and not isinstance(_supabase_admin_client, MockSupabaseClient):
        return _supabase_admin_client

    if settings.SUPABASE_URL and not settings.SUPABASE_URL.startswith("https://mock"):
        try:
            from supabase import create_client
            key = settings.admin_key
            if key and (key.startswith("eyJ") or key.startswith("sb_secret")):
                _supabase_admin_client = create_client(
                    settings.SUPABASE_URL,
                    key
                )
                return _supabase_admin_client
        except Exception as e:
            logger.warning(f"Could not connect to live Supabase admin client: {e}")

    _supabase_admin_client = MockSupabaseClient()
    return _supabase_admin_client


class MockSupabaseTable:
    def __init__(self, name: str, db_store: dict):
        self.name = name
        self.db_store = db_store
        if self.name not in self.db_store:
            self.db_store[self.name] = []

    def insert(self, data: Any):
        if isinstance(data, list):
            self.db_store[self.name].extend(data)
        else:
            self.db_store[self.name].append(data)
        return self

    def select(self, columns: str = "*"):
        return self

    def update(self, data: dict):
        return self

    def eq(self, column: str, value: Any):
        return self

    def delete(self):
        return self

    def execute(self):
        records = self.db_store.get(self.name, [])
        class MockResponse:
            def __init__(self, data):
                self.data = data
        return MockResponse(records)


class MockSupabaseClient:
    def __init__(self):
        self.db_store: Dict[str, List[dict]] = {}

    def table(self, table_name: str):
        return MockSupabaseTable(table_name, self.db_store)

    def rpc(self, fn_name: str, params: dict):
        class MockRPCResponse:
            def execute(self):
                class Resp:
                    data = []
                return Resp()
        return MockRPCResponse()

    @property
    def storage(self):
        class MockStorage:
            def from_(self, bucket: str):
                class MockBucket:
                    def upload(self, path: str, file_data: Any, file_options: Any = None):
                        return {"path": path}
                    def remove(self, paths: list):
                        return paths
                    def create_signed_url(self, path: str, expires_in: int):
                        return {"signedURL": f"http://localhost:8001/mock-storage/{path}"}
                return MockBucket()
        return MockStorage()
