import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile

from azure.core.exceptions import ResourceNotFoundError
import azure.storage.blob.aio
import pytest

from azaux.container_manager import ContainerManager

from .mocks import MockAzureCredential, MockBlob


@pytest.fixture
def container_manager(monkeypatch):
    return ContainerManager(
        container=os.environ["AZURE_STORAGE_CONTAINER"],
        account=os.environ["AZURE_STORAGE_ACCOUNT"],
        credential=MockAzureCredential(),
    )


@pytest.mark.asyncio
@pytest.mark.skipif(
    sys.version_info.minor < 10, reason="requires Python 3.10 or higher"
)
async def test_upload_get_names_download_and_remove(
    monkeypatch, mock_env, container_manager: ContainerManager
):
    with NamedTemporaryFile(suffix=".pdf") as temp_file:
        filepath = Path(temp_file.file.name)

        # 1. Upload a blob
        async def mock_exists(*args, **kwargs):
            return True

        monkeypatch.setattr(
            "azure.storage.blob.aio.ContainerClient.exists", mock_exists
        )

        async def mock_upload_blob(self, name: str, *args, **kwargs):
            assert name == filepath.name
            return azure.storage.blob.aio.BlobClient.from_blob_url(
                "https://test.blob.core.windows.net/test/test.pdf",
                credential=MockAzureCredential(),  # type: ignore
            )

        monkeypatch.setattr(
            "azure.storage.blob.aio.ContainerClient.upload_blob", mock_upload_blob
        )

        blob_url = await container_manager.upload_blob(filepath)
        assert blob_url == "https://test.blob.core.windows.net/test/test.pdf"

        # 2. Get blob names
        def mock_list_blob_names(*args, **kwargs):
            assert kwargs.get("name_starts_with") is None

            class AsyncBlobItemsIterator:
                def __init__(self, blob_name: str):
                    self.blob_names_list = [blob_name]

                def __aiter__(self):
                    return self

                async def __anext__(self):
                    if self.blob_names_list:
                        return self.blob_names_list.pop()
                    raise StopAsyncIteration

            return AsyncBlobItemsIterator(filepath.name)

        monkeypatch.setattr(
            "azure.storage.blob.aio.ContainerClient.list_blob_names",
            mock_list_blob_names,
        )

        assert [filepath.name] == await container_manager.get_blob_names()

        # 3. Download blob bytes and saving it to file
        async def mock_download_blob(self, name: str, *args, **kwargs):
            assert name == filepath.name
            return MockBlob()

        monkeypatch.setattr(
            "azure.storage.blob.aio.ContainerClient.download_blob", mock_download_blob
        )

        blob_bytes = await MockBlob().readall()
        assert await container_manager.download_blob(filepath.name) == blob_bytes

        save_path = Path(filepath.parent / "test.pdf")
        await container_manager.download_blob_to_file(filepath.name, save_path)
        with open(file=save_path, mode="rb") as f:
            assert f.read() == blob_bytes

        # 4. Remove blob
        async def mock_delete_blob(self, name: str, *args, **kwargs):
            assert name == filepath.name
            return True

        monkeypatch.setattr(
            "azure.storage.blob.aio.ContainerClient.delete_blob", mock_delete_blob
        )

        await container_manager.remove_blob(filepath.name)


@pytest.mark.asyncio
@pytest.mark.skipif(
    sys.version_info.minor < 10, reason="requires Python 3.10 or higher"
)
async def test_upload_create_and_error_when_no_container(
    monkeypatch, mock_env, container_manager: ContainerManager
):
    with NamedTemporaryFile(suffix=".pdf") as temp_file:
        filepath = Path(temp_file.file.name)

        # Set up mocks used by upload_blob
        async def mock_exists(*args, **kwargs):
            return False

        monkeypatch.setattr(
            "azure.storage.blob.aio.ContainerClient.exists", mock_exists
        )

        async def mock_create_container(*args, **kwargs):
            return

        monkeypatch.setattr(
            "azure.storage.blob.aio.ContainerClient.create_container",
            mock_create_container,
        )

        async def mock_upload_blob(self, name, *args, **kwargs):
            assert name == filepath.name
            return azure.storage.blob.aio.BlobClient.from_blob_url(
                "https://test.blob.core.windows.net/test/test.pdf",
                credential=MockAzureCredential(),  # type: ignore
            )

        monkeypatch.setattr(
            "azure.storage.blob.aio.ContainerClient.upload_blob", mock_upload_blob
        )

        # assert upload when create_by_default is True
        container_manager.create_by_default = True
        blob_url = await container_manager.upload_blob(filepath)
        assert blob_url == "https://test.blob.core.windows.net/test/test.pdf"

        # assert error when create_by_default is False
        container_manager.create_by_default = False
        with pytest.raises(ResourceNotFoundError):
            await container_manager.upload_blob(filepath)


@pytest.mark.asyncio
@pytest.mark.skipif(
    sys.version_info.minor < 10, reason="requires Python 3.10 or higher"
)
async def test_remove_error_if_no_container(
    monkeypatch, mock_env, container_manager: ContainerManager
):
    async def mock_exists(*args, **kwargs):
        return False

    monkeypatch.setattr("azure.storage.blob.aio.ContainerClient.exists", mock_exists)

    async def mock_delete_blob(*args, **kwargs):
        assert False, "delete_blob() shouldn't have been called"

    monkeypatch.setattr(
        "azure.storage.blob.aio.ContainerClient.delete_blob", mock_delete_blob
    )

    with pytest.raises(ResourceNotFoundError):
        await container_manager.remove_blob(blob_name="")


def test_storage_connection_string(mock_env, container_manager: ContainerManager):
    with pytest.raises(ValueError):
        container_manager.storage.from_connection_string("error_test")
    container_manager.storage.from_connection_string(
        "DefaultEndpointsProtocol=test;AccountName=test;AccountKey=test;"
    )
