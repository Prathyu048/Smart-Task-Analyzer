# tasks/tests.py
from django.test import TestCase
from .scoring import detect_cycles, score_task

class ScoringTests(TestCase):
    def test_detect_simple_cycle(self):
        tasks = [
            {"id": "t1", "dependencies": ["t2"]},
            {"id": "t2", "dependencies": ["t1"]}
        ]
        cycles = detect_cycles(tasks)
        self.assertTrue(any(set(cycle) == {"t1", "t2"} for cycle in cycles))

    def test_no_cycle_linear(self):
        tasks = [
            {"id": "a", "dependencies": []},
            {"id": "b", "dependencies": ["a"]},
            {"id": "c", "dependencies": ["b"]}
        ]
        cycles = detect_cycles(tasks)
        self.assertEqual(cycles, [])

    def test_score_task_basic(self):
        tasks = [
            {"id":"t1","title":"Fix login","due_date":"2025-11-30","estimated_hours":3,"importance":8,"dependencies":[]}
        ]
        tasks_by_id = {t["id"]: t for t in tasks}
        score, breakdown = score_task(tasks[0], tasks_by_id, today=None)
        self.assertIsInstance(score, float)
        self.assertIn("urgency", breakdown)
