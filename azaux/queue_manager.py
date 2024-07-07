import asyncio
from contextlib import asynccontextmanager

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.queue.aio import QueueServiceClient

from azaux.storage_resource import StorageResource, StorageResourceType


class QueueManager(StorageResource):
    """
    Class to manage sending messages to a given queue from the Queue Storage account

    :param queue: The name of the queue.
    :param account: The name of the Azure Storage account.
    :param credential: The credential used to authenticate the storage account.
    :param create_by_default: Whether to create the queue if it does not exist or raise an error.
    """

    def __init__(
        self,
        queue: str,
        account: str,
        credential: AzureNamedKeyCredential | AsyncTokenCredential,
        create_by_default: bool = False,
    ):
        self.queue = queue
        super().__init__(account, credential)
        self.create_by_default = create_by_default

    @property
    def resource_type(self) -> StorageResourceType:
        """Return the resource type"""
        return StorageResourceType.QUEUE

    @asynccontextmanager
    async def get_client(self):
        """Retrieve a client for the queue"""
        async with QueueServiceClient(
            self.endpoint, self.storage.credential
        ) as service_client:
            # NOTE: not exists() method for QueueClient
            if not service_client.list_queues(self.queue):
                if self.create_by_default:  # if queue does not exist, create it
                    await service_client.create_queue(self.queue)
                else:  # if queue does not exist, raise error
                    raise ResourceNotFoundError(f"Queue not found: '{self.queue}'")
            yield service_client.get_queue_client(self.queue)

    async def send_messages(self, instance_inputs: list[str]):
        """
        Send messages to the queue

        :param instance_inputs: The list of messages to send to the queue.
        """
        async with self.get_client() as queue_client:
            async with asyncio.TaskGroup() as tg:
                for input_msg in instance_inputs:
                    tg.create_task(queue_client.send_message(input_msg))  # type: ignore
