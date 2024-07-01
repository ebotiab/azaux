import asyncio
from contextlib import asynccontextmanager

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
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

    async def send_messages(self, instance_inputs: list[str]):
        """Send messages to the queue"""
        async with self.get_client() as queue_client:
            send_message_tasks = [
                queue_client.send_message(input_msg) for input_msg in instance_inputs
            ]
            await asyncio.gather(*send_message_tasks)

    @asynccontextmanager
    async def get_client(self):
        async with QueueServiceClient(
            self.endpoint, self.storage.credential
        ) as service_client:
            yield service_client.get_queue_client(self.queue)
