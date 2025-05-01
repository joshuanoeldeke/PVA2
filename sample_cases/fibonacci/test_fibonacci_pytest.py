import pytest
from fibonacci.fibonacci import fib

@ pytest.mark.parametrize("n, expected", [
    (0, 0),
    (1, 1),
    (2, 1),
    (3, 2),
    (10, 55)
])
def test_fib_values(n, expected):
    assert fib(n) == expected

def test_negative():
    with pytest.raises(ValueError):
        fib(-1)
