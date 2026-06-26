import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import Config
from shared.models import Cursor


class CursorStore:
    def __init__(
        self,
        config: Config
    ):
        self.config = config

    def get_cursor(
        self,
        id: str,
        guid: str
    ) -> Cursor:
        with sqlite3.connect(self.config.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT *
                FROM _cursors
                WHERE id = ? AND guid = ?;
                """,
                (id, guid),
            ).fetchone()
        return Cursor.from_row(dict(row)) if row is not None else None

    def update_cursors(
        self,
        id: str,
        guid: str,
        slug: str,
        name: str,
        page: int,
        size: int,
    ) -> None:
        update_at = datetime.now(ZoneInfo("Europe/Paris")).strftime("%Y-%m-%d %H:%M")
        with sqlite3.connect(self.config.db_path) as conn:
            conn.execute(
                """
                INSERT INTO _cursors (id, guid, slug, name, page, size, update_at)
                VALUES (:id, :guid, :slug, :name, :page, :size, :update_at)
                ON CONFLICT(id, guid)
                DO UPDATE SET
                    slug = excluded.slug,
                    name = excluded.name,
                    page = excluded.page,
                    size = excluded.size,
                    update_at = excluded.update_at;
                """,
                (id, guid, slug, name, page, size, update_at),
            )
