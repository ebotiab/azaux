# import pytest
# from unittest.mock import AsyncMock, MagicMock
# from azaux.container_manager import ContainerManager


# @pytest.mark.asyncio
# async def test_list_blobs(container_manager: ContainerManager):
#     # Mock the list_blobs method of the container client
#     container_manager.get_client.return_value.list_blobs.return_value = [
#         MagicMock(name="blob1", spec=["name"]),
#         MagicMock(name="blob2", spec=["name"]),
#     ]

#     # Call the list_blobs method of ContainerManager
#     result = await container_manager.list_blobs()

#     # Check the result
#     assert result == ["blob1", "blob2"]


# @pytest.mark.asyncio
# async def test_download_blob(container_manager: ContainerManager):
#     # Mock the download_blob method of the blob client
#     blob_client = container_manager.get_blob_client.return_value
#     blob_client.download_blob.return_value.readall.return_value = b"test-data"

#     # Call the download_blob method of ContainerManager
#     result = await container_manager.download_blob("test-filepath")

#     # Check the result
#     assert result == b"test-data"


# @pytest.mark.asyncio
# async def test_download_blob_to_file(container_manager: ContainerManager, tmp_path):
#     # Mock the download_blob method of ContainerManager
#     container_manager.download_blob = AsyncMock(return_value=b"test-data")

#     # Call the download_blob_to_file method of ContainerManager
#     filepath = tmp_path / "test-file.txt"
#     await container_manager.download_blob_to_file(filepath)

#     # Check if the file exists and contains the correct data
#     assert filepath.exists()
#     assert filepath.read_bytes() == b"test-data"


# @pytest.mark.asyncio
# async def test_upload_blob(container_manager: ContainerManager):
#     # Mock the upload_blob method of the blob client
#     blob_client = container_manager.get_blob_client.return_value

#     # Call the upload_blob method of ContainerManager
#     await container_manager.upload_blob("test-filepath", b"test-data")

#     # Check if the upload_blob method of the blob client was called with the correct arguments
#     blob_client.upload_blob.assert_called_once_with(b"test-data")


# @pytest.mark.asyncio
# async def test_upload_blob_from_file(container_manager: ContainerManager):
#     # Mock the upload_blob method of ContainerManager
#     container_manager.upload_blob = AsyncMock()

#     # Call the upload_blob_from_file method of ContainerManager
#     await container_manager.upload_blob_from_file(
#         "test-filepath", "test-local-filepath"
#     )

#     # Check if the upload_blob method of ContainerManager was called with the correct arguments
#     container_manager.upload_blob.assert_called_once_with(
#         "test-filepath", b"test-local-filedata"
#     )


# @pytest.mark.asyncio
# async def test_delete_blob(container_manager: ContainerManager):
#     # Mock the delete_blob method of the blob client
#     blob_client = container_manager.get_blob_client.return_value

#     # Call the delete_blob method of ContainerManager
#     await container_manager.delete_blob("test-filepath")

#     # Check if the delete_blob method of the blob client was called with the correct arguments
#     blob_client.delete_blob.assert_called_once()
