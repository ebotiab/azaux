from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from enum import Enum
import re

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.credentials_async import AsyncTokenCredential


class StorageResourceType(str, Enum):
    TABLE = "table"
    QUEUE = "queue"
    BLOB = "blob"


class StorageManager:
    """
    A class that manages storage resources in Azure Storage.

    :param account: The name of the Azure Storage account.
    :param credential: The credential used to authenticate the storage account.
    """

    # Connection string format for Azure Storage
    STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix=core.windows.net"

    def __init__(
        self, account: str, credential: str | AzureNamedKeyCredential | AsyncTokenCredential
    ):
        self.account = account
        self.credential = credential

    def get_enpoint(self, resource_type: StorageResourceType):
        """
        Retrieves the endpoint URL for the specified storage resource type.

        :param resource_type: The type of storage resource.
        :return: The endpoint URL for the specified storage resource type.
        """
        return f"https://{self.account}.{resource_type.value}.core.windows.net"

    @classmethod
    def from_connection_string(cls, connection_string: str) -> "StorageManager":
        """
        Creates a StorageManager instance from an Azure Storage connection string.

        :param connection_string: The Azure Storage connection string.
        :return: A new instance of the StorageManager class.
        :raise ValueError: If the connection string is invalid.
        """
        match = re.match(
            r"DefaultEndpointsProtocol=(.*);AccountName=(.*);AccountKey=(.*);",
            connection_string,
        )
        if not match:
            raise ValueError("Invalid connection string")
        _, account, key = match.groups()
        return cls(account, AzureNamedKeyCredential(account, key))


class StorageResource(ABC):
    """
    Abstract class for managing storage resources in Azure Storage.

    :param account: The name of the Azure Storage account.
    :param credential: The credential used to authenticate the storage account.
    """

    def __init__(
        self,
        account: str,
        credential: str | AzureNamedKeyCredential | AsyncTokenCredential,
    ):
        self.storage = StorageManager(account, credential)

    @property
    def endpoint(self):
        """Return the endpoint URL for the storage resource"""
        return self.storage.get_enpoint(self.resource_type)

    @property
    @abstractmethod
    def resource_type(self) -> StorageResourceType:
        """Return the resource type"""
        pass

    @asynccontextmanager
    @abstractmethod
    async def get_client(self):
        """Retrieve a client for the storage resource"""
        yield None
