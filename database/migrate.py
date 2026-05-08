"""Migration script for FinTrack database.
When the schema changes, after update schema.sql, then run script to apply the changes to MySQL.
It reads the SQL file and executes the statements one by one"""

import sys
from pathlib import Path

import pymysql

# add backend/ to the path to import settings from there
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import settings


def split_statements(sql: str) -> list[str]:
    """Split a SQL string into separate statements as pymysql can only run one statement at a time"""

    statements: list[str] = []
    buf: str = ""
    for line in sql.splitlines():
        stripped = line.strip()
        # skip blank lines and SQL comments
        if not stripped or stripped.startswith("--"):
            continue
        buf += f"{line}\n"

        # if statement ends with ";" save it as a SQL command
        if buf.rstrip().endswith(";"):
            statements.append(buf.rstrip().removesuffix(";").strip())
            buf = ""
    if buf.strip():
        statements.append(buf.strip())
    return statements


def main(path: Path) -> None:
    """Run each SQL statement in the file"""
    statements = split_statements(path.read_text(encoding="utf-8"))

    # MySQL connection
    conn = pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        charset="utf8mb4",
    )
    try:
        # run each statement one by one
        with conn.cursor() as cur:
            for statement in statements:
                cur.execute(statement)
        # save the changes to database
        conn.commit()
        print("Migration completed")
    finally:
        conn.close()


if __name__ == "__main__":
    default = ROOT / "database" / "schema.sql"
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else default)
