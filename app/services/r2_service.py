import logging
from typing import Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger("knora.storage")


class R2StorageService:
    def __init__(self):
        self.endpoint_url = settings.CLOUDFLARE_R2_ENDPOINT_URL
        self.access_key = settings.CLOUDFLARE_R2_ACCESS_KEY_ID
        self.secret_key = settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY
        self.bucket_name = settings.CLOUDFLARE_R2_BUCKET_NAME
        
        self.boto_config = Config(
            region_name="auto",
            signature_version="s3v4",
            connect_timeout=10,
            read_timeout=10
        )

    def _get_client(self):
        """Returns an initialized S3 client configured for Cloudflare R2."""
        return boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=self.boto_config
        )

    def upload_file(
        self,
        file_bytes: bytes,
        object_key: str,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Uploads file bytes to Cloudflare R2 bucket.
        Returns the object_key upon success.
        """
        try:
            client = self._get_client()
            client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_bytes,
                ContentType=content_type
            )
            logger.info(f"Successfully uploaded {object_key} to R2 bucket {self.bucket_name}")
            return object_key
        except ClientError as e:
            logger.error(f"Failed to upload {object_key} to R2: {e}")
            raise e

    def generate_presigned_url(self, object_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generates a presigned URL to view/download a private object from R2.
        """
        try:
            client = self._get_client()
            url = client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {object_key}: {e}")
            return None

    def delete_file(self, object_key: str) -> bool:
        """
        Deletes an object from the Cloudflare R2 bucket.
        """
        try:
            client = self._get_client()
            client.delete_object(Bucket=self.bucket_name, Key=object_key)
            logger.info(f"Successfully deleted {object_key} from R2 bucket {self.bucket_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete {object_key} from R2: {e}")
            return False


r2_storage_service = R2StorageService()
