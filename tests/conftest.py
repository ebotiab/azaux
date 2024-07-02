# import pytest
# from unittest.mock import AsyncMock, MagicMock
# from azaux.container_manager import ContainerManager


# @pytest.fixture
# def container_manager():
#     # Mock the necessary dependencies
#     credential = AsyncMock()
#     container_client = MagicMock()
#     container_client.get_blob_client.return_value = MagicMock()
#     container_client.get_blob_client.return_value.exists.return_value = True
#     blob_service_client = MagicMock()
#     blob_service_client.get_container_client.return_value = container_client

#     # Create an instance of ContainerManager with the mocked dependencies
#     manager = ContainerManager(
#         container="test-container",
#         account="test-account",
#         credential=credential,
#         resource_group="test-resource-group",
#     )
#     manager.get_client = AsyncMock(return_value=blob_service_client)
#     return manager
