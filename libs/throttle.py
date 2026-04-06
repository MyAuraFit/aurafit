from __future__ import annotations

import random
from functools import wraps
from threading import Lock
from typing import Optional, Callable, Any

from kivy.clock import Clock
from kivy.logger import Logger


class CallLimiter:
    """
    Limits the number of callable executions within defined constraints.

    The CallLimiter class is designed to control the frequency of callable
    executions, often for situations where rate limiting, backoff, or threading
    safety is required. It supports options for thread safety, scheduling with
    exponential backoff, and jitter (randomized delay) for deferred executions.

    :ivar max_calls: Maximum number of allowable calls before blocking.
    :type max_calls: int
    :ivar calls: Number of calls made so far.
    :type calls: int
    :ivar scheduled: Whether calls should be executed immediately or scheduled later.
    :type scheduled: bool
    :ivar backoff_base: Base duration used for calculating exponential backoff delay.
    :type backoff_base: float
    :ivar backoff_cap: Maximum cap for backoff delay.
    :type backoff_cap: float
    :ivar jitter: Configuration for applying randomness in backoff delay calculation.
    :type jitter: str
    """

    def __init__(
        self,
        *,
        max_calls: int,
        thread_safe: bool = False,
        scheduled: bool = False,
        backoff_base: float = 0.0,  # seconds; 0 means "schedule immediately"
        backoff_cap: float = 5.0,  # seconds
        jitter: str = "full",  # "full" | "equal" | "none"
        log_name: Optional[str] = None,  # label in logs
    ):
        if max_calls < 0:
            raise ValueError("max_calls must be >= 0")
        if backoff_base < 0 or backoff_cap < 0:
            raise ValueError("backoff_base/backoff_cap must be >= 0")
        if jitter not in {"full", "equal", "none"}:
            raise ValueError("jitter must be one of: 'full', 'equal', 'none'")

        self.max_calls = max_calls
        self.calls = 0

        self.scheduled = scheduled
        self.backoff_base = backoff_base
        self.backoff_cap = backoff_cap
        self.jitter = jitter

        self._lock: Optional[Lock] = Lock() if thread_safe else None
        self._log_name = log_name or "CallLimiter"

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Decide (atomically if needed)
            if self._lock is None:
                allowed, call_index = self._consume_slot()
            else:
                with self._lock:
                    allowed, call_index = self._consume_slot()

            if not allowed:
                Logger.warning(
                    f"{self._log_name}: max_calls reached ({self.max_calls}). "
                    f"Blocked call to {getattr(func, '__name__', 'callable')}."
                )
                return None

            # Allowed: either run now, or schedule all calls
            if not self.scheduled:
                print("not scheduled")
                return func(*args, **kwargs)

            delay = self._compute_delay(call_index)
            print("delayed", delay)
            # Defer execution to Kivy event loop (UI-safe)
            Clock.schedule_once(lambda dt: func(*args, **kwargs), delay)
            return None  # execution happens later

        # Control hooks
        wrapper.calls_made = self.calls_made
        wrapper.reset = self.reset
        wrapper.remaining = self.remaining
        wrapper.decrement = self.decrement
        wrapper.next_delay = self.next_delay
        wrapper.backoff_state = self.backoff_state
        wrapper.in_progress = self.in_progress
        return wrapper

    # ---------- internals ----------

    def _consume_slot(self) -> tuple[bool, int]:
        """
        Returns (allowed, call_index).
        call_index is 1-based index for the allowed call (1..max_calls).
        """
        if self.calls >= self.max_calls:
            return False, self.calls
        self.calls += 1
        return True, self.calls

    def _compute_delay(self, call_index: int) -> float:
        """
        Exponential backoff delay for scheduled calls.
        If backoff_base == 0, delay is always 0 (schedule immediately).
        """
        if self.backoff_base == 0:
            return 0.0

        exp = self.backoff_base * (2 ** (call_index - 1))
        cap = min(exp, self.backoff_cap)

        if cap <= 0:
            return 0.0
        if self.jitter == "none":
            return cap
        if self.jitter == "equal":
            half = cap / 2.0
            return half + random.random() * half
        return random.random() * cap  # full jitter

    # ---------- public API ----------

    def reset(self) -> None:
        if self._lock is None:
            self.calls = 0
        else:
            with self._lock:
                self.calls = 0

    def remaining(self) -> int:
        if self._lock is None:
            return self.max_calls - self.calls
        with self._lock:
            return self.max_calls - self.calls

    def calls_made(self) -> int:
        if self._lock is None:
            return self.calls
        with self._lock:
            return self.calls

    def decrement(self) -> None:
        if self._lock is None:
            self.calls = max(0, self.calls - 1)
        else:
            with self._lock:
                self.calls = max(0, self.calls - 1)

    def next_delay(self) -> float:
        """
        Returns the delay (in seconds) that would be applied
        to the *next allowed call* if scheduling is enabled.

        If max_calls is already reached, returns 0.0 because
        no further calls will be scheduled.
        """
        if self._lock is None:
            calls = self.calls
        else:
            with self._lock:
                calls = self.calls

        # No more calls allowed → nothing will be scheduled
        if calls >= self.max_calls:
            return 0.0

        # call_index is 1-based
        call_index = calls + 1
        return self._compute_delay(call_index)

    def backoff_state(self) -> dict:
        """
        Returns a snapshot of the limiter/backoff state.
        Useful for debugging, logging, or UI inspection.
        """
        if self._lock is None:
            calls = self.calls
        else:
            with self._lock:
                calls = self.calls

        return {
            "max_calls": self.max_calls,
            "calls_used": calls,
            "remaining_calls": self.max_calls - calls,
            "scheduled": self.scheduled,
            "next_delay": (
                self._compute_delay(calls + 1)
                if calls < self.max_calls and self.scheduled
                else 0.0
            ),
            "backoff_base": self.backoff_base,
            "backoff_cap": self.backoff_cap,
            "jitter": self.jitter,
        }

    def in_progress(self) -> bool:
        return 0 < self.calls_made() < self.max_calls
