
import sys
import pytest


def pytest_addoption(parser):
    parser.addoption("--runlong", action="store_true",
                     help="run long running tests")

def pytest_configure(config):
    sys._called_from_test = True

def pytest_unconfigure(config):
    del sys._called_from_test
