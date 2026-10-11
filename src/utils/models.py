from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any

class SearchRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    query: str = Field(min_length=1, max_length=1000)
    top_k: Optional[int] = Field(default=None, ge=1, description='Optional legacy limit. Omit it to rank the entire filtered dataset.')
    state: Optional[str]=None; city: Optional[str]=None; season: Optional[str]=None; weather: Optional[str]=None; network_condition: Optional[str]=None

class DiagnosisRequest(SearchRequest):
    include_predictions: bool=True

class FeedbackRequest(BaseModel):
    query: str = Field(min_length=1,max_length=1000)
    incident_id: str = Field(min_length=1,max_length=50)
    rating: int = Field(ge=1, le=5)
    comment: Optional[str]=Field(default=None,max_length=1000)

class SearchResult(BaseModel):
    incident_id: str; score: float; semantic_score: float; lexical_score: float; metadata: Dict[str, Any]; document: str
