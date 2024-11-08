import os
from unittest.mock import AsyncMock, MagicMock

from azure.data.tables import TableEntity
import pytest

from azaux.table_manager import TableManager
from .mocks import MockAzureCredential


@pytest.fixture
def table_manager(monkeypatch):
    return TableManager(
        table=os.environ["AZURE_STORAGE_TABLE"],
        account=os.environ["AZURE_STORAGE_ACCOUNT"],
        api_key=MockAzureCredential(),  # type: ignore
    )


@pytest.mark.asyncio
async def test_upsert_entity(table_manager: TableManager):
    # Mock the TableServiceClient and TableClient
    table_client_mock = AsyncMock()
    table_service_client_mock = MagicMock()
    table_service_client_mock.get_table_client.return_value = table_client_mock

    # Define the entity data
    entity_data = {
        "PartitionKey": "partition_key",
        "RowKey": "row_key",
        "Value": "value",
    }

    # Call the upsert_entity method
    await table_manager.upsert_entity(entity_data)

    # Assert that the upsert_entity method of the table client was called with the correct arguments
    table_client_mock.upsert_entity.assert_called_once_with(entity=entity_data)


@pytest.mark.asyncio
async def test_retrieve_table_entities(table_manager: TableManager):
    # Mock the TableServiceClient and TableClient
    table_client_mock = AsyncMock()
    table_service_client_mock = MagicMock()
    table_service_client_mock.get_table_client.return_value = table_client_mock

    # Define the query
    query = "PartitionKey eq 'partition_key'"

    # Call the retrieve_table_entities method
    entities = await table_manager.retrieve_table_entities(query)

    # Assert that the query_entities method of the table client was called with the correct arguments
    table_client_mock.query_entities.assert_called_once_with(query_filter=query)

    # Assert that the returned entities match the expected entities
    assert entities == table_client_mock.query_entities.return_value


@pytest.mark.asyncio
async def test_remove_table_entity(table_manager: TableManager):
    # Mock the TableServiceClient and TableClient
    table_client_mock = AsyncMock()
    table_service_client_mock = MagicMock()
    table_service_client_mock.get_table_client.return_value = table_client_mock

    # Define the entity
    entity = {
        "PartitionKey": "partition_key",
        "RowKey": "row_key",
        "Value": "value",
    }
    table_entity = TableEntity(entity)

    # Call the remove_table_entity method
    await table_manager.remove_table_entity(table_entity)

    # Assert that the delete_entity method of the table client was called with the correct arguments
    table_client_mock.delete_entity.assert_called_once_with(
        partition_key=entity["PartitionKey"], row_key=entity["RowKey"]
    )
