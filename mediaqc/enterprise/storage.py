"""Storage backend contracts for enterprise MAM."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class StorageObject:
    uri: str
    backend: str
    exists: bool


class StorageBackend:
    name = "base"

    def resolve(self, uri: str) -> StorageObject:
        raise NotImplementedError


class NASStorageBackend(StorageBackend):
    name = "nas"

    def resolve(self, uri: str) -> StorageObject:
        path = Path(uri).expanduser()
        return StorageObject(uri=str(path), backend=self.name, exists=path.exists())


class S3StorageBackend(StorageBackend):
    name = "s3"

    def resolve(self, uri: str) -> StorageObject:
        return StorageObject(uri=uri, backend=self.name, exists=uri.startswith("s3://"))


class AzureStorageBackend(StorageBackend):
    name = "azure"

    def resolve(self, uri: str) -> StorageObject:
        return StorageObject(uri=uri, backend=self.name, exists=uri.startswith("azure://") or uri.startswith("https://"))


class GoogleDriveStorageBackend(StorageBackend):
    name = "google_drive"

    def resolve(self, uri: str) -> StorageObject:
        return StorageObject(uri=uri, backend=self.name, exists=uri.startswith("gdrive://") or "drive.google.com" in uri)


class WebDAVStorageBackend(StorageBackend):
    name = "webdav"

    def resolve(self, uri: str) -> StorageObject:
        return StorageObject(uri=uri, backend=self.name, exists=uri.startswith("webdav://") or uri.startswith("https://"))


def get_storage_backend(name: str) -> StorageBackend:
    backends: dict[str, StorageBackend] = {
        "nas": NASStorageBackend(),
        "s3": S3StorageBackend(),
        "azure": AzureStorageBackend(),
        "google_drive": GoogleDriveStorageBackend(),
        "webdav": WebDAVStorageBackend(),
    }
    try:
        return backends[name]
    except KeyError as exc:
        raise ValueError(f"Unknown storage backend: {name}") from exc
