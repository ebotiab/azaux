from contextlib import asynccontextmanager
from pathlib import Path

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
        max_single_put_size=4 * 1024 * 1024,
    ):
        self.container = container
        super().__init__(account, credential)
        self.max_single_put_size = max_single_put_size

    @property
    def resource_type(self) -> StorageResourceType:
        return StorageResourceType.BLOB

    @asynccontextmanager
    async def get_client(self, check_exists=True):
        max_put = self.max_single_put_size
        async with BlobServiceClient(
            self.endpoint, self.storage.credential, max_single_put_size=max_put
        ) as service_client:
            container_client = service_client.get_container_client(self.container)
            if check_exists and not await container_client.exists():
                raise ResourceNotFoundError(f"Container not found: '{self.container}'")
            yield container_client

    @asynccontextmanager
    async def get_blob_client(self, blob_name: str, check_exists=True):
        async with self.get_client() as container_client:
            blob_client = container_client.get_blob_client(blob_name)
            if check_exists and not await blob_client.exists():
                raise ResourceNotFoundError(f"Blob file not found: '{blob_name}'")
            yield blob_client

    async def list_blobs(self, **kwargs) -> list[str]:
        """Retrieve a list of blob files in the container"""
        async with self.get_client() as container_client:
            blob_names_list: list[str] = []
            async for blob_properties in container_client.list_blobs(**kwargs):
                blob_names_list.append(blob_properties.name)
            return blob_names_list

    async def download_blob(self, blob_name: str):
        """Retrieve data from a given blob file"""
        async with self.get_blob_client(blob_name) as blob_client:
            blob = await blob_client.download_blob()
            return await blob.readall()

    async def download_blob_to_file(self, filepath: str):
        """Download a blob file to the local filesystem"""
        with open(file=filepath, mode="wb") as f:
            blob_data = await self.download_blob(filepath)
            f.write(blob_data)

    async def upload_blob(self, filepath: Path, **kwargs) -> str:
        """Upload a file to a given blob file, overwriting if it already exists"""
        async with self.get_client() as container_client:
            with open(file=filepath, mode="rb") as f:
                blob_client = await container_client.upload_blob(
                    filepath.name, f, overwrite=True, **kwargs
                )
        return blob_client.url

    async def remove_blob(self, blob_name: str, **kwargs):
        """Delete a given blob file"""
        async with self.get_blob_client(blob_name) as blob_client:
            await blob_client.delete_blob(**kwargs)
