import os
from pathlib import Path
from typing import Optional

import boto3
from botocore.client import Config as BotoConfig

from app.core.config import settings


class Storage:
    def __init__(self):
        self.backend = settings.storage_backend.lower()
        if self.backend == "s3":
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.s3_endpoint or None,
                aws_access_key_id=settings.s3_access_key,
                aws_secret_access_key=settings.s3_secret_key,
                config=BotoConfig(signature_version="s3v4"),
                region_name=settings.s3_region or "us-east-1",
            )
            self.bucket = settings.s3_bucket
        else:
            Path(settings.local_storage_dir).mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: bytes, content_type: Optional[str] = None) -> str:
        if self.backend == "s3":
            extra = {"ContentType": content_type} if content_type else {}
            self._client.put_object(Bucket=self.bucket, Key=key, Body=data, **extra)
            base = settings.public_base_url.rstrip("/") if settings.public_base_url else ""
            return f"{base}/{key}" if base else key
        else:
            path = Path(settings.local_storage_dir) / key
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            return f"/files/{key}"

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        if self.backend == "s3":
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        return None
