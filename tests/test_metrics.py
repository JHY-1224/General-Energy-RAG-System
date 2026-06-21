import unittest

from app.evaluation.retrieval_metrics import calculate_retrieval_metrics


class RetrievalMetricsTest(unittest.TestCase):
    def test_ranked_metrics(self):
        metrics = calculate_retrieval_metrics(["doc_a", "doc_b"], ["doc_b"])
        self.assertEqual(metrics["hit_at_5"], 1.0)
        self.assertEqual(metrics["recall_at_5"], 1.0)
        self.assertEqual(metrics["mrr"], 0.5)

    def test_duplicate_document_ids_do_not_inflate_ndcg(self):
        metrics = calculate_retrieval_metrics(["doc_a", "doc_a", "doc_b"], ["doc_a", "doc_b"], {"doc_a": 3, "doc_b": 2})

        self.assertLessEqual(metrics["ndcg_at_5"], 1.0)


if __name__ == "__main__":
    unittest.main()
