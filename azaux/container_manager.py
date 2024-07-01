from contextlib import asynccontextmanager

from azure.core.credentials_async import AsyncTokenCredential
from azure.core.exceptions import ResourceNotFoundError
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

    async def list_blobs(self, **kwargs) -> list[str]:
        """Retrieve a list of blob files in the container"""
        async with self.get_client() as container_client:
            blob_list = []
            async for blob in container_client.list_blobs(**kwargs):
                blob_list.append(blob.name)
            return blob_list

    async def download_blob(self, filepath: str, **kwargs) -> bytes:
        """Retrieve data from a given blob file"""
        async with self.get_blob_client(filepath) as blob_client:
            try:
                blob = await blob_client.download_blob(**kwargs)
                blob_data = await blob.readall()
            except ResourceNotFoundError:
                raise FileNotFoundError(f"Blob file not found: '{filepath}'")
            return blob_data

    async def download_blob_to_file(self, filepath: str):
        """Download a blob file to the local filesystem"""
        with open(file=filepath, mode="wb") as f:
            blob_data = await self.download_blob(filepath)
            f.write(blob_data)

    async def upload_blob(self, filepath: str, data: bytes, **kwargs):
        """Upload data to a given blob file"""
        async with self.get_blob_client(filepath) as blob_client:
            await blob_client.upload_blob(data, **kwargs)

    async def upload_blob_from_file(self, filepath: str, local_filepath: str, **kwargs):
        """Upload a file to a given blob file"""
        with open(file=local_filepath, mode="rb") as f:
            data = f.read()
            await self.upload_blob(filepath, data, **kwargs)

    async def delete_blob(self, filepath: str, **kwargs):
        """Delete a given blob file"""
        async with self.get_blob_client(filepath) as blob_client:
            await blob_client.delete_blob(**kwargs)
