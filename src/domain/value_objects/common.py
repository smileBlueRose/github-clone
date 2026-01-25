from pydantic import BaseModel, Field


class Pagination(BaseModel):
    limit: int = Field(le=100, default=10)
    offset: int = Field(ge=0, default=0)
