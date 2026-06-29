import unittest

from app.evaluation.ragas_diagnostics import diagnose_scores


class RagasDiagnosticsTest(unittest.TestCase):
    def test_low_recall_is_primary_retrieval_miss(self):
        diagnosis = diagnose_scores(
            {
                "faithfulness": 0.62,
                "answer_relevancy": 0.85,
                "context_precision": 0.76,
                "context_recall": 0.48,
            }
        )

        self.assertEqual(diagnosis["primary_failure_type"], "retrieval_miss")
        self.assertIn("提高 top_k", diagnosis["suggestions"])

    def test_healthy_scores_return_no_failure_type(self):
        diagnosis = diagnose_scores(
            {
                "faithfulness": 0.91,
                "answer_relevancy": 0.86,
                "context_precision": 0.82,
                "context_recall": 0.79,
            }
        )

        self.assertIsNone(diagnosis["primary_failure_type"])


if __name__ == "__main__":
    unittest.main()
