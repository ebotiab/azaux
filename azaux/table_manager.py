from contextlib import asynccontextmanager

from azure.core.credentials import AzureNamedKeyCredential
from azure.data.tables import TableEntity
from azure.data.tables.aio import TableServiceClient

from claims_runner.azure_helper.storage_resource import (
    StorageResourceType,
    StorageResource,
)


class TableManager(StorageResource):
    """
    Class to manage retrieving and upsert table entities from a given table from the Table Storage account
    """

    def __init__(
        self,
        table: str,
        account: str,
        credential: AzureNamedKeyCredential,  # | AsyncTokenCredential,
    ):
        self.table = table
        super().__init__(account, credential)

    @property
    def resource_type(self):
        return StorageResourceType.TABLE

    @asynccontextmanager
    async def get_client(self):
        async with TableServiceClient(
            self.endpoint, credential=self.storage.credential
        ) as service_client:
            yield service_client.get_table_client(self.table)

    async def upsert_entity(self, entity_data: dict):
        """Upload a table entity to the table storage account with the given PineconeReference"""
        async with self.get_client() as table_client:
            await table_client.upsert_entity(entity=entity_data)

    async def retrieve_table_entities(self, query: str):
        """Retrieve all table entities that match a given query"""
        table_entities_list: list[TableEntity] = []
        async with self.get_client() as table_client:
            async for table_ent in table_client.query_entities(query_filter=str(query)):
                table_entities_list.append(table_ent)
        return table_entities_list

    async def remove_table_entity(self, entity: TableEntity):
        """Remove a table entity from the table storage account"""
        async with self.get_client() as table_client:
            await table_client.delete_entity(
                partition_key=entity["PartitionKey"], row_key=entity["RowKey"]
            )
