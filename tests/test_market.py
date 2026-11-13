"""Unit tests for agent-auction-task-allocator."""
import unittest
from agent_auction_task_allocator.market import DoubleAuctionMarket, TaskOrder, WorkerBid

class TestDoubleAuctionMarket(unittest.TestCase):
    def setUp(self):
        self.market = DoubleAuctionMarket()

    def test_single_match(self):
        t = TaskOrder("t1", "b1", "Code Review", max_price=50.0, max_latency_ms=500.0)
        w = WorkerBid("w1", min_price=30.0, est_latency_ms=250.0, reputation=0.9)
        self.market.submit_task(t)
        self.market.register_worker(w)
        matches = self.market.match_tasks()
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].worker_id, "w1")
        self.assertEqual(matches[0].clearing_price, 40.0)

    def test_reject_incompatible_price(self):
        t = TaskOrder("t2", "b1", "RAG Pipeline", max_price=20.0, max_latency_ms=500.0)
        w = WorkerBid("w2", min_price=30.0, est_latency_ms=250.0)
        self.market.submit_task(t)
        self.market.register_worker(w)
        matches = self.market.match_tasks()
        self.assertEqual(len(matches), 0)

    def test_prefer_higher_utility_worker(self):
        t = TaskOrder("t3", "b1", "SQL Optimization", max_price=60.0, max_latency_ms=1000.0)
        w1 = WorkerBid("w_slow", min_price=20.0, est_latency_ms=900.0, reputation=0.5)
        w2 = WorkerBid("w_fast", min_price=30.0, est_latency_ms=200.0, reputation=0.99)
        self.market.submit_task(t)
        self.market.register_worker(w1)
        self.market.register_worker(w2)
        matches = self.market.match_tasks()
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].worker_id, "w_fast")

if __name__ == "__main__":
    unittest.main()
