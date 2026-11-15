from pydantic import BaseModel, Field

class SourceItem(BaseModel):
    document_id: str
    content: str
    score: float | None = None
    metadata: dict = Field(default_factory=dict)

class QueryResponse(BaseModel):
    answer: str
    thread_id: str
    agent: str
    sources: list[SourceItem] = Field(default_factory=list)
    analysis_metrics: dict = Field(default_factory=dict)

class HealthResponse(BaseModel):
    status: str
    application: str
    version: str
