from abc import ABC, abstractmethod
from enum import Enum
import re

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.credentials_async import AsyncTokenCredential


class StorageResourceType(str, Enum):
    TABLE = "table"
    QUEUE = "queue"
    BLOB = "blob"


class StorageManager:

    STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix=core.windows.net"

    def __init__(
        self, account: str, credential: AzureNamedKeyCredential | AsyncTokenCredential
    ):
        self.account = account
        self.credential = credential

    def get_enpoint(self, resource_type: StorageResourceType):
        return f"https://{self.account}.{resource_type.value}.core.windows.net"

    @classmethod
    def from_connection_string(cls, table: str, connection_string: str):
        """Create a TableManager instance from an Azure Storage connection string"""
        match = re.match(
            r"DefaultEndpointsProtocol=(.*);AccountName=(.*);AccountKey=(.*);",
            connection_string,
        )
        if not match:
            raise ValueError("Invalid connection string")
        _, account, key = match.groups()
        return cls(account, AzureNamedKeyCredential(account, key))


class StorageResource(ABC):

    def __init__(
        self,
        account: str,
        credential: AzureNamedKeyCredential | AsyncTokenCredential,
    ):
        self.storage = StorageManager(account, credential)

    @property
    def endpoint(self):
        return self.storage.get_enpoint(self.resource_type)

    @property
    @abstractmethod
    def resource_type(self) -> StorageResourceType:
        pass
