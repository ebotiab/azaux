from contextlib import asynccontextmanager

from azure.core.credentials_async import AsyncTokenCredential
from azure.storage.blob.aio import BlobServiceClient

from azaux.storage_resource import StorageResource, StorageResourceType


class ContainerManager(StorageResource):
    """
    Class to manage retrieving blob data from a given blob file
    """

    def __init__(
        self,
        container: str,
        account: str,
        credential: AsyncTokenCredential,
        resource_group: str,
    ):
        self.resource_group = resource_group
        self.container = container
        super().__init__(account, credential)

    @property
    def resource_type(self) -> StorageResourceType:
        return StorageResourceType.BLOB

    @asynccontextmanager
    async def get_client(self):
        async with BlobServiceClient(
            self.endpoint, self.storage.credential
        ) as service_client:
            yield service_client.get_container_client(self.container)

    @asynccontextmanager
    async def get_blob_client(self, filepath: str):
        async with self.get_client() as container_client:
            yield container_client.get_blob_client(filepath)
