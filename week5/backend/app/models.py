from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String, Table, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Many-to-many join table: notes ↔ tags
note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    # Explicit index on tag_id alone so "find all notes with tag X" joins are efficient
    Index("ix_note_tags_tag_id", "tag_id"),
)


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(
        String(200), nullable=False, index=True
    )  # speeds up ORDER BY title / prefix searches
    content = Column(Text, nullable=False)
    tags = relationship("Tag", secondary=note_tags, back_populates="notes", lazy="selectin")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    notes = relationship("Note", secondary=note_tags, back_populates="tags", lazy="selectin")


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    completed = Column(
        Boolean, default=False, nullable=False, index=True
    )  # speeds up completed filter
