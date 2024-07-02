# import pytest
# from unittest.mock import AsyncMock, MagicMock
# from azure.core.credentials import AzureNamedKeyCredential
# from azure.data.tables.aio import TableServiceClient
# from azaux.table_manager import TableManager


# @pytest.mark.asyncio
# async def test_upsert_entity():
#     # Mock the TableServiceClient and TableClient
#     table_client_mock = AsyncMock()
#     table_service_client_mock = MagicMock()
#     table_service_client_mock.get_table_client.return_value = table_client_mock

#     # Create a TableManager instance
#     table_manager = TableManager(
#         table="my_table",
#         account="my_account",
#         credential=AzureNamedKeyCredential("my_key"),
#     )

#     # Set the endpoint and storage credential
#     table_manager.endpoint = "https://my_storage_account.table.core.windows.net"
#     table_manager.storage.credential = AzureNamedKeyCredential("my_key")

#     # Define the entity data
#     entity_data = {
#         "PartitionKey": "partition_key",
#         "RowKey": "row_key",
#         "Value": "value",
#     }

#     # Call the upsert_entity method
#     await table_manager.upsert_entity(entity_data)

#     # Assert that the upsert_entity method of the table client was called with the correct arguments
#     table_client_mock.upsert_entity.assert_called_once_with(entity=entity_data)
