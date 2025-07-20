from sqlmodel import SQLModel, Field, Column
from uuid import UUID, uuid4          # <-- already brings UUID into scope
from datetime import datetime
import sqlalchemy.dialects.postgresql as pg


class User(SQLModel, table=True):
    __tablename__ = "user_accounts"
    __table_args__ = {"schema": "kool_assembly"}

    uid: UUID = Field(                
        default_factory=uuid4,
        sa_column=Column(
            pg.UUID(as_uuid=True),    # as_uuid=True lets SQLAlchemy hand you UUID objects
            primary_key=True,
            unique=True,
            nullable=False,
        ),
    )

    username: str
    first_name: str
    last_name: str
    is_verified: bool = Field(default=False)
    email: str
    password_hash: str =Field(exclude=True)  # Exclude from model dumps, e.g., in responses

    created_at: datetime = Field(
        default_factory=datetime.utcnow,        # utcnow avoids TZ surprises
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False),
    )

    def __repr__(self) -> str:                  
        return f"<User {self.username}>"
