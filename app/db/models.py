from sqlalchemy import Boolean, Column, DateTime, Float, Integer, MetaData, String, Table, Text

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True),
    Column("email", String, nullable=False, unique=True),
    Column("name", String, nullable=True),
    Column("password_hash", String, nullable=True),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime),
)

journal_entries = Table(
    "journal_entries",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", String, default="anonymous"),
    Column("content", Text, nullable=False),
    Column("created_at", DateTime),
    Column("updated_at", DateTime, nullable=True),
    Column("mood_label", String, nullable=True),
    Column("themes", Text, nullable=True),    # JSON list e.g. ["work stress", "relationships"]
    Column("entities", Text, nullable=True),   # JSON list e.g. ["Sarah", "gym", "therapy"]
    Column("sentiment_score", Float, nullable=True),
    Column("summary", Text, nullable=True),
)

mood_logs = Table(
    "mood_logs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", String, default="anonymous"),
    Column("message", Text, nullable=False),
    Column("mood_label", String),
    Column("timestamp", DateTime),
    Column("source_type", String, nullable=True),   # "chat", "journal", "explicit"
    Column("source_id", Integer, nullable=True),     # FK to messages.id or journal_entries.id
    Column("confidence", String, nullable=True),     # "high", "medium", "low"
)

chat_sessions = Table(
    "chat_sessions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", String, default="anonymous"),
    Column("title", String, nullable=True),
    Column("created_at", DateTime),
    Column("updated_at", DateTime, nullable=True),
)

messages = Table(
    "messages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", String, default="anonymous"),
    Column("session_id", Integer, nullable=True),
    Column("role", String, nullable=False),
    Column("content", Text, nullable=False),
    Column("intent", String, nullable=True),
    Column("tool_class", String, nullable=True),
    Column("created_at", DateTime),
    Column("updated_at", DateTime, nullable=True),
    Column("original_content", Text, nullable=True),
)

therapy_sessions = Table(
    "therapy_sessions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", String, default="anonymous"),
    Column("session_number", Integer, nullable=True),
    Column("date", String, nullable=True),
    Column("issues_discussed", Text, default="[]"),
    Column("learnings", Text, default=""),
    Column("action_items", Text, default="[]"),
    Column("techniques", Text, default="[]"),
    Column("therapist_notes", Text, nullable=True),
    Column("raw_notes", Text, nullable=True),
    Column("created_at", DateTime),
    Column("updated_at", DateTime, nullable=True),
)

reminders = Table(
    "reminders",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", String, default="anonymous"),
    Column("message", Text, nullable=False),
    Column("frequency", String, default="daily"),
    Column("time_of_day", String, default="20:00"),
    Column("last_sent", DateTime, nullable=True),
    Column("active", Boolean, default=True),
    Column("created_at", DateTime),
)
