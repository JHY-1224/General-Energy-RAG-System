from fastapi import APIRouter, HTTPException

from app.api.dependencies import engine
from app.core.models import IngestRequest


router = APIRouter(prefix="/api/v2", tags=["RAG v2 Ingest"])


@router.post("/ingest")
def ingest(payload: IngestRequest):
    try:
        return engine.ingest(payload)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
