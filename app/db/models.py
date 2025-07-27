
from sqlalchemy import Table, Column, Integer, String, Text, TIMESTAMP, MetaData, Time, Boolean

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True),
    Column("email", String, nullable=False, unique=True),
    Column("name", String, nullable=True),
    Column("is_active", Boolean, default=True),
    Column("created_at", TIMESTAMP),
)


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


reminders = Table(
    "reminders",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", String, default="anonymous"),
    Column("message", Text, nullable=False),
    Column("frequency", String, default="daily"),
    Column("time_of_day", Time, default="20:00"),
    Column("last_sent", TIMESTAMP, nullable=True),
    Column("active", Boolean, default=True),
    Column("created_at", TIMESTAMP)
)