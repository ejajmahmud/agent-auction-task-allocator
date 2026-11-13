"""CLI for agent-auction-task-allocator."""
import sys
import argparse
from .market import DoubleAuctionMarket, TaskOrder, WorkerBid

def main():
    parser = argparse.ArgumentParser(description="Agent Auction Task Allocator CLI")
    parser.add_argument("--demo", action="store_true", help="Run double auction matching demo")
    args = parser.parse_args()

    if args.demo:
        market = DoubleAuctionMarket()
        market.submit_task(TaskOrder("task-101", "buyer-agent", "Summarize paper", max_price=45.0, max_latency_ms=400.0))
        market.register_worker(WorkerBid("worker-gpu-fast", min_price=35.0, est_latency_ms=180.0, reputation=0.95))
        market.register_worker(WorkerBid("worker-cpu-budget", min_price=20.0, est_latency_ms=350.0, reputation=0.88))
        allocations = market.match_tasks()
        print(f"[+] Task auction matched {len(allocations)} allocation(s):")
        for alloc in allocations:
            print(f"    Task {alloc.task_id} -> {alloc.worker_id} @ ${alloc.clearing_price} (score: {alloc.score})")
    else:
        parser.print_help()
    sys.exit(0)

if __name__ == "__main__":
    main()
