import unittest

from app.core.models import RagChunk
from app.graph_retrieval.graph_hybrid_retriever import GraphHybridRetriever
from app.graph_retrieval.graph_index_builder import GraphIndexBuilder
from app.graph_retrieval.graph_metrics import calculate_graph_metrics
from app.graph_retrieval.graph_store import GraphStore


class GraphRetrievalTest(unittest.TestCase):
    def setUp(self):
        self.chunks = [
            RagChunk(
                doc_id="wind_doc",
                chunk_id="wind_001",
                content="AccY 表示机舱横向振动，异常时需要检查塔架共振和 0-5Hz 频谱能量异常。",
                metadata={"domain": "wind_oam"},
            ),
            RagChunk(
                doc_id="load_doc",
                chunk_id="load_001",
                content="lag_96 用于日周期建模，是负荷预测的关键输入特征。",
                metadata={"domain": "load_forecast"},
            ),
            RagChunk(
                doc_id="storage_doc",
                chunk_id="storage_001",
                content="EMS、BMS、PCS 共同支撑储能运行管理，SOC 受充放电策略约束并服务削峰填谷。",
                metadata={"domain": "storage_ems"},
            ),
        ]
        self.store = GraphStore()
        self.stats = GraphIndexBuilder(self.store).build_graph_from_chunks(self.chunks, persist=False)

    def test_builds_energy_entities_and_relations(self):
        self.assertGreaterEqual(self.stats["entity_count"], 10)
        relation_types = {item.relation_type for item in self.store.relations.values()}
        self.assertIn("INDICATES", relation_types)
        self.assertIn("INPUT_FEATURE_OF", relation_types)
        self.assertIn("CONSTRAINED_BY", relation_types)
        self.assertIn("SUPPORTS", relation_types)

    def test_hybrid_graph_returns_reasoning_and_sources(self):
        result = GraphHybridRetriever(self.store).retrieve(
            "AccY 超限为什么可能关联塔架共振？",
            mode="hybrid_graph",
            domain="wind_oam",
            max_hops=2,
        )
        names = {item.name for item in result["entities"]}
        self.assertIn("AccY", names)
        self.assertIn("塔架共振", names)
        self.assertTrue(result["relations"])
        self.assertTrue(result["reasoning_path"])
        self.assertIn("wind_001", result["related_chunk_ids"])
        self.assertIn("【图增强关系上下文】", result["graph_context"])

    def test_graph_metrics_are_bounded(self):
        metrics = calculate_graph_metrics(["e1"], ["r1"], ["hop 1", "hop 2"], ["c1"], ["e1"], ["r1"], ["c1"])
        self.assertTrue(all(0.0 <= value <= 1.0 for value in metrics.values()))


if __name__ == "__main__":
    unittest.main()
