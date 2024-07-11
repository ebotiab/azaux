import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import overload

from azure.core.credentials_async import AsyncTokenCredential

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob.aio import BlobServiceClient

from azaux.storage_resource import StorageResource, StorageResourceType


# Rest of the code...
class ContainerManager(StorageResource):
    """
    Class to manage retrieving blob data from a given blob file.

    :param container: The name of the container.
    :param account: The name of the Azure Storage account.
    :param credential: The credential used to authenticate the storage account.
    :param create_by_default: Whether to create the container if it does not exist or raise an error.
    :param max_single_put_size: The maximum size of a single put request in bytes.
    """

    def __init__(
        self,
        container: str,
        account: str,
        credential: str | AsyncTokenCredential,
        create_by_default: bool = False,
        max_single_put_size=4 * 1024 * 1024,
    ):
        self.container = container
        super().__init__(account, credential)
        self.create_by_default = create_by_default
        self.max_single_put_size = max_single_put_size

    @property
    def resource_type(self) -> StorageResourceType:
        """Return the resource type"""
        return StorageResourceType.BLOB

    @asynccontextmanager
    async def get_client(self):
        """Retrieve a client for the container"""
        max_put = self.max_single_put_size
        async with BlobServiceClient(
            self.endpoint, self.storage.credential, max_single_put_size=max_put
        ) as service_client:
            container_client = service_client.get_container_client(self.container)
            if not await container_client.exists():
                if self.create_by_default:  # if container does not exist, create it
                    await container_client.create_container()
                else:  # if container does not exist, raise error
                    raise ResourceNotFoundError(
                        f"Container not found: '{self.container}'"
                    )
            yield container_client

    @asynccontextmanager
    async def get_blob_client(self, blob_name: str):
        """
        Retrieve a client for a given blob file

        :param blob_name: The name of the blob file.
        """
        async with self.get_client() as container_client:
            blob_client = container_client.get_blob_client(blob_name)
            if not await blob_client.exists():
                raise ResourceNotFoundError(f"Blob file not found: '{blob_name}'")
            yield blob_client

    async def get_blob_names(self, **kwargs):
        """Retrieve a list of blob files in the container"""
        async with self.get_client() as container_client:
            return [b async for b in container_client.list_blob_names(**kwargs)]

    @overload
    async def download_blob(self, blob_name: str, encoding: None, **kw) -> bytes: ...

    @overload
    async def download_blob(self, blob_name: str, encoding: str, **kw) -> str: ...

    async def download_blob(
        self, blob_name: str, encoding: None | str, **kw
    ) -> bytes | str:
        """
        Retrieve data from a given blob file within the container in bytes.

        :param blob_name: The name of the blob file.
        """
        async with self.get_client() as container_client:
            blob = await container_client.download_blob(
                blob_name, encoding=encoding, **kw
            )
            return await blob.readall()

    async def download_blob_to_file(self, blob_name: str, filepath: Path | None = None):
        """
        Download a blob file to the local filesystem with blob_name as default path.

        :param blob_name: The name of the blob file.
        :param filepath: The path to save the blob file to
        """
        filepath = filepath or Path(blob_name)
        with open(file=filepath, mode="wb") as f:
            f.write(await self.download_blob(blob_name, encoding=None))

    async def upload_blob(
        self, filepath: Path, blob_name: str | None = None, **kwargs
    ) -> str:
        """
        Upload a file to a blob with the filepath as default name.

        :param filepath: The path to the file to upload.
        :param blob_name: The name of the blob file.
        """
        async with self.get_client() as container_client:
            with open(file=filepath, mode="rb") as f:
                blob_name = blob_name or filepath.name
                blob_client = await container_client.upload_blob(
                    blob_name, f, overwrite=True, **kwargs
                )
        return blob_client.url

    async def upload_blobs(
        self, filepaths: list[Path], blob_names: list[str] | None = None, **kwargs
    ):
        """
        Upload multiple files to blobs with the filepaths as default names.

        :param filepaths: The paths to the files to upload.
        :param blob_names: The names of the blob files.
        """
        paths = zip(filepaths, blob_names or [f.name for f in filepaths])
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(self.upload_blob(fp, n)) for fp, n in paths]
        return [t.result() for t in tasks]

    async def remove_blob(self, blob_name: str, **kwargs):
        """
        Delete a given blob

        :param blob_name: The name of the blob file.
        """
        async with self.get_client() as container_client:
            await container_client.delete_blob(blob_name, **kwargs)
