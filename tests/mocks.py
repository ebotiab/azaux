from collections import namedtuple

from azure.core.credentials_async import AsyncTokenCredential

MOCK_EMBEDDING_DIMENSIONS = 1536
MOCK_EMBEDDING_MODEL_NAME = "text-embedding-ada-002"

MockToken = namedtuple("MockToken", ["token", "expires_on", "value"])


class MockAzureCredential(AsyncTokenCredential):

    async def get_token(self, uri):
        return MockToken("", 9999999999, "")


class MockAzureCredentialExpired(AsyncTokenCredential):

    def __init__(self):
        self.access_number = 0

    async def get_token(self, uri):
        self.access_number += 1
        if self.access_number == 1:
            return MockToken("", 0, "")
        else:
            return MockToken("", 9999999999, "")
