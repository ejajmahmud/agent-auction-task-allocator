"""Core double auction task allocation mechanism."""
import time
from typing import List, Dict, Optional, Tuple, Any

class TaskOrder:
    def __init__(self, task_id: str, buyer_id: str, description: str, max_price: float, max_latency_ms: float, quality_threshold: float = 0.5):
        self.task_id = task_id
        self.buyer_id = buyer_id
        self.description = description
        self.max_price = max_price
        self.max_latency_ms = max_latency_ms
        self.quality_threshold = quality_threshold
        self.timestamp = time.time()

class WorkerBid:
    def __init__(self, worker_id: str, min_price: float, est_latency_ms: float, reputation: float = 1.0, capabilities: Optional[List[str]] = None):
        self.worker_id = worker_id
        self.min_price = min_price
        self.est_latency_ms = est_latency_ms
        self.reputation = reputation
        self.capabilities = set(capabilities or [])
        self.timestamp = time.time()

class AllocationMatch:
    def __init__(self, task_id: str, buyer_id: str, worker_id: str, clearing_price: float, expected_latency_ms: float, score: float):
        self.task_id = task_id
        self.buyer_id = buyer_id
        self.worker_id = worker_id
        self.clearing_price = clearing_price
        self.expected_latency_ms = expected_latency_ms
        self.score = score
        self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "buyer_id": self.buyer_id,
            "worker_id": self.worker_id,
            "clearing_price": round(self.clearing_price, 2),
            "expected_latency_ms": self.expected_latency_ms,
            "score": round(self.score, 4)
        }

class DoubleAuctionMarket:
    """Continuous double auction and utility-maximizing clearing engine for agent task allocations."""

    def __init__(self, platform_fee_pct: float = 0.02):
        self.platform_fee_pct = platform_fee_pct
        self.pending_tasks: Dict[str, TaskOrder] = {}
        self.registered_workers: Dict[str, WorkerBid] = {}
        self.completed_allocations: List[AllocationMatch] = []

    def submit_task(self, task: TaskOrder):
        self.pending_tasks[task.task_id] = task

    def register_worker(self, bid: WorkerBid):
        self.registered_workers[bid.worker_id] = bid

    def remove_worker(self, worker_id: str):
        self.registered_workers.pop(worker_id, None)

    def match_tasks(self) -> List[AllocationMatch]:
        matched = []
        for task_id, task in list(self.pending_tasks.items()):
            eligible_workers = []
            for wid, bid in self.registered_workers.items():
                if bid.min_price <= task.max_price and bid.est_latency_ms <= task.max_latency_ms:
                    # Score function: trade-off between price surplus, speed, and reputation
                    price_surplus = (task.max_price - bid.min_price) / max(task.max_price, 1e-6)
                    speed_surplus = (task.max_latency_ms - bid.est_latency_ms) / max(task.max_latency_ms, 1e-6)
                    score = (price_surplus * 0.4) + (speed_surplus * 0.3) + (bid.reputation * 0.3)
                    eligible_workers.append((score, bid))

            if eligible_workers:
                eligible_workers.sort(key=lambda x: x[0], reverse=True)
                best_score, best_bid = eligible_workers[0]
                # Clearing price: mid-point between bid ask and task reserve
                clearing_price = (task.max_price + best_bid.min_price) / 2.0
                allocation = AllocationMatch(
                    task_id=task.task_id,
                    buyer_id=task.buyer_id,
                    worker_id=best_bid.worker_id,
                    clearing_price=clearing_price,
                    expected_latency_ms=best_bid.est_latency_ms,
                    score=best_score
                )
                matched.append(allocation)
                self.completed_allocations.append(allocation)
                del self.pending_tasks[task_id]

        return matched
