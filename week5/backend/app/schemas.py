from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class TagAttachRequest(BaseModel):
    tag_id: int


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class NoteUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    tags: list[TagRead] = []


class NoteSearchPage(BaseModel):
    items: list[NoteRead]
    total: int
    page: int
    page_size: int


class ExtractionResult(BaseModel):
    tags: list[str]
    action_items: list[str]


class ActionItemCreate(BaseModel):
    description: str = Field(min_length=1)


class ActionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    completed: bool


class BulkCompleteRequest(BaseModel):
    ids: list[int]


class ActionItemsPage(BaseModel):
    items: list[ActionItemRead]
    total: int
    page: int
    page_size: int
