# content of conftest.py
import pytest

def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true",
        help="run slow tests(not video)")
    parser.addoption("--vidtest", action="store_true",
        help="run slow video tests")
