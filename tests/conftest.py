import os
from unittest import mock
import pytest


@pytest.fixture()
def mock_env(monkeypatch):
    with mock.patch.dict(os.environ, clear=True):
        monkeypatch.setenv("AZURE_STORAGE_CONTAINER", "test-storage-container")
        monkeypatch.setenv("AZURE_STORAGE_ACCOUNT", "test-storage-account")
        yield
