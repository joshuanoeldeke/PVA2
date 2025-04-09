# tests/test_calculator_pytest.py
import pytest
import sys
import os

# Add the tests directory to the path to find example_test_module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example_test_module import Calculator


@pytest.fixture
def calculator():
    return Calculator()


def test_add(calculator):
    assert calculator.add(3, 5) == 8
    assert calculator.add(-1, 1) == 0
    assert calculator.add(-1, -1) == -2


def test_subtract(calculator):
    assert calculator.subtract(5, 3) == 2
    assert calculator.subtract(1, 1) == 0
    assert calculator.subtract(-1, -1) == 0


def test_multiply(calculator):
    assert calculator.multiply(3, 5) == 15
    assert calculator.multiply(-1, 1) == -1
    assert calculator.multiply(-1, -1) == 1


def test_divide(calculator):
    assert calculator.divide(6, 3) == 2
    assert calculator.divide(5, 2) == 2.5
    with pytest.raises(ValueError):
        calculator.divide(1, 0)
