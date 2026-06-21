from contextlib import contextmanager
from time import perf_counter


class LatencyTracker:
    def __init__(self) -> None:
        self.values: dict[str, float] = {}

    @contextmanager
    def track(self, name: str):
        started = perf_counter()
        yield
        self.values[name] = round((perf_counter() - started) * 1000, 3)
