import os
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def normalize_url(url: str) -> str:
    return url.strip().rstrip("/").lower()


def load_cache() -> set:
    try:
        result = supabase.table("blacklist").select("url").execute()
        return set(row["url"] for row in result.data)
    except Exception as e:
        print(f"  ✗ Помилка завантаження кешу: {e}")
        return set()


def is_in_blacklist(cache: set, url: str) -> bool:
    return normalize_url(url) in cache


def add_to_blacklist(cache: set, url: str, user_id: int) -> bool:
    normalized = normalize_url(url)
    try:
        supabase.table("blacklist").insert({
            "url": normalized,
            "added_by": user_id
        }).execute()
        cache.add(normalized)
        return True
    except Exception:
        return False