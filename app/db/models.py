
from sqlalchemy import Table, Column, Integer, String, Text, TIMESTAMP, MetaData

metadata = MetaData()

journal_entries = Table(
    "journal_entries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", String, default="anonymous"),
    Column("content", Text, nullable=False),
    Column("created_at", TIMESTAMP)
)

mood_logs = Table(
    "mood_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", String, default="anonymous"),
    Column("message", Text, nullable=False),
    Column("mood_label", String),
    Column("timestamp", TIMESTAMP)
)