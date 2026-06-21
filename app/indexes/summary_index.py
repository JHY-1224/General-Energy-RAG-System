from app.core.models import RagChunk


class SummaryIndex:
    def build(self, chunks: list[RagChunk]) -> list[RagChunk]:
        summaries: list[RagChunk] = []
        for chunk in chunks:
            summary = chunk.content[:320]
            summaries.append(RagChunk(doc_id=chunk.doc_id, chunk_id=f"summary_{chunk.chunk_id}", content=summary, metadata={**chunk.metadata, "chunk_type": "Summary", "source_chunk_id": chunk.chunk_id}))
        return summaries
