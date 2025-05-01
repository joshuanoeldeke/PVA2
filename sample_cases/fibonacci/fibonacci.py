def fib(n: int) -> int:
    """Compute the n-th Fibonacci number (0-indexed)."""
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a