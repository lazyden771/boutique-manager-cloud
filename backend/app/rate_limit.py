"""
Minimal login-attempt rate limiter. Deliberately simple: an in-memory
dict, no external service. Good enough for a small number of known shops
hitting one server process - it resets on restart and won't work correctly
if you ever run multiple server instances behind a load balancer (each
instance would count separately). If this app grows past that, swap this
for a shared store (Redis) keyed the same way.

Locks out an email after too many failed attempts in a short window,
rather than after every single failed password - a legitimate typo
shouldn't lock anyone out on the first try.
"""

import time
from collections import defaultdict
from threading import Lock

MAX_ATTEMPTS = 5
WINDOW_SECONDS = 15 * 60  # 15 minutes
LOCKOUT_SECONDS = 15 * 60  # once locked out, stay locked for 15 minutes

_attempts: dict[str, list[float]] = defaultdict(list)
_lock = Lock()


def _prune_old(email: str, now: float) -> None:
    _attempts[email] = [t for t in _attempts[email] if now - t < WINDOW_SECONDS]


def is_locked_out(email: str) -> bool:
    now = time.time()
    with _lock:
        _prune_old(email, now)
        return len(_attempts[email]) >= MAX_ATTEMPTS


def record_failed_attempt(email: str) -> None:
    now = time.time()
    with _lock:
        _prune_old(email, now)
        _attempts[email].append(now)


def clear_attempts(email: str) -> None:
    """Called on a successful login - a real login shouldn't stay
    penalized for earlier typos once they get it right."""
    with _lock:
        _attempts.pop(email, None)


def _reset_all_for_tests() -> None:
    """Test-only helper - the module-level dict otherwise leaks state
    between test functions since it's a process-wide singleton."""
    with _lock:
        _attempts.clear()
