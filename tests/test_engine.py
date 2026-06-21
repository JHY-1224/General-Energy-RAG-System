import unittest

from app.core.engine import ConfigurableRagEngine
from app.core.models import QueryOptions, QueryRequest, RagChunk


class EngineTest(unittest.TestCase):
    def test_trace_contains_pipeline_details(self):
        engine = ConfigurableRagEngine()
        engine.add_chunks([RagChunk(doc_id="doc_wind", chunk_id="chunk_accy", content="AccY 表示机舱 Y 向加速度。", metadata={"domain": "风电故障诊断", "chunk_type": "变量解释"})])
        trace = engine.query(QueryRequest(question="AccY 是什么？", options=QueryOptions(metadata_filter={"domain": "风电故障诊断"})))
        self.assertTrue(trace.trace_id)
        self.assertTrue(trace.retrieved_docs)
        self.assertIn("total", trace.latency_ms)

    def test_remove_document_rebuilds_indexes(self):
        engine = ConfigurableRagEngine()
        engine.add_chunks(
            [
                RagChunk(doc_id="doc_remove", chunk_id="chunk_remove", content="temporary content"),
                RagChunk(doc_id="doc_keep", chunk_id="chunk_keep", content="persistent content"),
            ]
        )

        removed = engine.remove_document("doc_remove")

        self.assertEqual(removed, 1)
        self.assertEqual([chunk.doc_id for chunk in engine.chunks], ["doc_keep"])
        self.assertNotIn("doc_remove", {hit.doc_id for hit in engine.vector_index.search("temporary", 5)})


if __name__ == "__main__":
    unittest.main()
