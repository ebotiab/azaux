from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from enum import StrEnum, auto
import re

from azure.core.credentials import AzureNamedKeyCredential


def conn_string_to_creds(connection_string: str) -> AzureNamedKeyCredential:
    """
    Creates a AzureNamedKeyCredential instance from an Azure Storage connection string.

    :param connection_string: The Azure Storage connection string.
    :return: A new instance of the AzureNamedKeyCredential class.
    :raise ValueError: If the connection string is invalid.
    """
    pattern = r"DefaultEndpointsProtocol=(.*);AccountName=(.*);AccountKey=(.*);"
    match = re.match(pattern, connection_string)
    if not match:
        raise ValueError("Invalid connection string")
    _, account, key = match.groups()
    return AzureNamedKeyCredential(account, key)


class StorageResourceType(StrEnum):
    table = auto()
    queue = auto()
    blob = auto()


class StorageResource(ABC):
    """
    Abstract class for managing storage resources in Azure Storage.

    :param account: The name of the Azure Storage account.
    :param credential: The credential used to authenticate the storage account.
    """

    def __init__(self, account: str, api_key: str):
        self.account = account
        self.api_key = api_key

    @property
    def credential(self):
        return AzureNamedKeyCredential(self.account, self.api_key)

    @property
    @abstractmethod
    def resource_type(self) -> StorageResourceType:
        """Return the resource type"""
        pass

    @property
    def endpoint(self):
        """Return the endpoint URL for the storage resource"""
        return f"https://{self.account}.{self.resource_type.value}.core.windows.net"

    @asynccontextmanager
    @abstractmethod
    async def get_client(self):
        """Retrieve a client for the storage resource"""
        yield None
