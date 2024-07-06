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
    """

    def __init__(
        self,
        queue: str,
        account: str,
        credential: AzureNamedKeyCredential | AsyncTokenCredential,
    ):
        self.queue = queue
        super().__init__(account, credential)

    @property
    def resource_type(self) -> StorageResourceType:
        return StorageResourceType.QUEUE

    @asynccontextmanager
    async def get_client(self, check_exists: bool = True):
        async with QueueServiceClient(
            self.endpoint, self.storage.credential
        ) as service_client:
            # NOTE: not exists() method for QueueClient
            if check_exists and not service_client.list_queues(self.queue):
                raise ResourceNotFoundError(f"Queue not found: '{self.queue}'")
            yield service_client.get_queue_client(self.queue)

    async def send_messages(self, instance_inputs: list[str]):
        """Send messages to the queue"""
        async with self.get_client() as queue_client:
            async with asyncio.TaskGroup() as tg:
                for input_msg in instance_inputs:
                    tg.create_task(queue_client.send_message(input_msg))  # type: ignore
