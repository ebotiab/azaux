import os

import pytest
from unittest.mock import AsyncMock

from azure.core.exceptions import ResourceNotFoundError

from azaux.queue_manager import QueueManager
from .mocks import MockAzureCredential


@pytest.fixture
def queue_manager():
    return QueueManager(
        queue=os.environ["AZURE_STORAGE_QUEUE"],
        account=os.environ["AZURE_STORAGE_ACCOUNT"],
        credential=MockAzureCredential(),  # type: ignore
    )


@pytest.mark.asyncio
async def test_send_messages(queue_manager: QueueManager):
    # Arrange
    queue = "myqueue"
    instance_inputs = ["message1", "message2"]

    queue_client_mock = AsyncMock()
    queue_client_mock.send_message = AsyncMock()

    queue_service_client_mock = AsyncMock()
    queue_service_client_mock.get_queue_client.return_value = queue_client_mock
    queue_service_client_mock.list_queues.return_value = []

    queue_manager.get_client = AsyncMock(return_value=queue_service_client_mock)

    # Act
    await queue_manager.send_messages(instance_inputs)

    # Assert
    queue_manager.get_client.assert_awaited_once()
    queue_service_client_mock.list_queues.assert_awaited_once_with(queue)
    queue_client_mock.send_message.assert_awaited_with("message1")
    queue_client_mock.send_message.assert_awaited_with("message2")


@pytest.mark.asyncio
async def test_send_messages_queue_exists(queue_manager: QueueManager):
    # Arrange
    queue = "myqueue"
    instance_inputs = ["message1", "message2"]

    queue_client_mock = AsyncMock()
    queue_client_mock.send_message = AsyncMock()

    queue_service_client_mock = AsyncMock()
    queue_service_client_mock.get_queue_client.return_value = queue_client_mock
    queue_service_client_mock.list_queues.return_value = [queue]

    queue_manager.get_client = AsyncMock(return_value=queue_service_client_mock)

    # Act
    await queue_manager.send_messages(instance_inputs)

    # Assert
    queue_manager.get_client.assert_awaited_once()
    queue_service_client_mock.list_queues.assert_awaited_once_with(queue)
    queue_client_mock.send_message.assert_awaited_with("message1")
    queue_client_mock.send_message.assert_awaited_with("message2")


@pytest.mark.asyncio
async def test_send_messages_create_queue(queue_manager: QueueManager):
    # Arrange
    queue = "myqueue"
    instance_inputs = ["message1", "message2"]

    queue_client_mock = AsyncMock()
    queue_client_mock.send_message = AsyncMock()

    queue_service_client_mock = AsyncMock()
    queue_service_client_mock.get_queue_client.return_value = queue_client_mock
    queue_service_client_mock.list_queues.return_value = []

    queue_manager.get_client = AsyncMock(return_value=queue_service_client_mock)

    # Act
    await queue_manager.send_messages(instance_inputs)

    # Assert
    queue_manager.get_client.assert_awaited_once()
    queue_service_client_mock.list_queues.assert_awaited_once_with(queue)
    queue_service_client_mock.create_queue.assert_awaited_once_with(queue)
    queue_client_mock.send_message.assert_awaited_with("message1")
    queue_client_mock.send_message.assert_awaited_with("message2")


@pytest.mark.asyncio
async def test_send_messages_queue_not_found(queue_manager: QueueManager):
    # Arrange
    instance_inputs = ["message1", "message2"]

    queue_service_client_mock = AsyncMock()
    queue_service_client_mock.list_queues.return_value = []

    queue_manager.get_client = AsyncMock(return_value=queue_service_client_mock)

    # Act & Assert
    with pytest.raises(ResourceNotFoundError):
        await queue_manager.send_messages(instance_inputs)
