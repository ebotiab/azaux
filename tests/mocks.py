from collections import namedtuple

from azure.core.credentials_async import AsyncTokenCredential

MOCK_EMBEDDING_DIMENSIONS = 1536
MOCK_EMBEDDING_MODEL_NAME = "text-embedding-ada-002"

MockToken = namedtuple("MockToken", ["token", "expires_on", "value"])


class MockBlob:

    def __init__(self):
        self.properties = ""
        
    async def readall(self):
        return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\xdac\xfc\xcf\xf0\xbf\x1e\x00\x06\x83\x02\x7f\x94\xad\xd0\xeb\x00\x00\x00\x00IEND\xaeB`\x82"


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
