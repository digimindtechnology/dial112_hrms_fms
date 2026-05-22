import mimetypes
import os
import urllib
from datetime import datetime
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from django.http import HttpResponse

from DmtHrmsFmsApp.settings import (
    AWS_S3_ENDPOINT_URL,
    AWS_S3_REGION_NAME,
    FILE_UPLOAD_STORAGE,
    MEDIA_ROOT,
    MEDIA_URL,
    S3_BUCKET_NAME,
    S3_FOLDER,
    S3_URL,
    aws_access_key_id,
    aws_secret_access_key,
)


def _s3_kwargs():
    kwargs = {
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key,
        'region_name': AWS_S3_REGION_NAME,
        'config': Config(signature_version='s3v4'),
    }
    if AWS_S3_ENDPOINT_URL:
        kwargs['endpoint_url'] = AWS_S3_ENDPOINT_URL
    return kwargs


def _s3_resource():
    return boto3.resource('s3', **_s3_kwargs())


def _s3_client():
    return boto3.client('s3', **_s3_kwargs())


def _storage_prefix():
    return (S3_FOLDER or '').strip('/')


def _build_storage_key(tenant_id, directory, file_name):
    parts = [_storage_prefix(), str(tenant_id), directory.strip('/'), file_name]
    return '/'.join(part for part in parts if part)


def _build_file_name(upload_file, file_name=''):
    file_extension = Path(upload_file.name).suffix
    safe_suffix = Path(file_name).stem if file_name else Path(upload_file.name).stem
    safe_suffix = safe_suffix.replace(' ', '_')
    return f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{safe_suffix}{file_extension}"


def GetFileUrl(file_path):
    if not file_path:
        return ''
    if file_path.startswith(('http://', 'https://', MEDIA_URL, '/')):
        return file_path
    return f"{S3_URL or ''}{file_path}"


class S3DirectoryManager:
    @staticmethod
    def create(directory_name):
        _s3_resource().Bucket(S3_BUCKET_NAME).put_object(Key=directory_name.rstrip('/') + '/')
        return directory_name

    @staticmethod
    def rename(old_directory, new_directory):
        bucket = S3_BUCKET_NAME
        old_directory = old_directory.rstrip('/') + '/'
        new_directory = new_directory.rstrip('/') + '/'
        client = _s3_client()
        response = client.list_objects_v2(Bucket=bucket, Prefix=old_directory)
        if 'Contents' in response:
            for obj in response['Contents']:
                new_key = obj['Key'].replace(old_directory, new_directory, 1)
                client.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': obj['Key']}, Key=new_key)
                client.delete_object(Bucket=bucket, Key=obj['Key'])
        return new_directory

    @staticmethod
    def delete(directory_name):
        bucket = S3_BUCKET_NAME
        client = _s3_client()
        response = client.list_objects_v2(Bucket=bucket, Prefix=directory_name.rstrip('/') + '/')
        if 'Contents' in response:
            for obj in response['Contents']:
                client.delete_object(Bucket=bucket, Key=obj['Key'])
        return directory_name


def UploadFileLocalSystem(tenantId, directory, uploadFile, fileName=''):
    try:
        file_name = _build_file_name(uploadFile, fileName)
        directory_path = os.path.join(MEDIA_ROOT, str(tenantId), directory.strip('/'))
        save_file = os.path.join(directory_path, file_name)
        os.makedirs(directory_path, exist_ok=True)

        if hasattr(uploadFile, 'seek'):
            uploadFile.seek(0)

        with open(save_file, 'wb') as destination:
            for chunk in uploadFile.chunks():
                destination.write(chunk)
        return f"{MEDIA_URL}{tenantId}/{directory.strip('/')}/{file_name}"
    except Exception as e:
        print("Local Upload Error:", e)
        return ''


def UploadFileS3Server(tenantId, directory, uploadFile, fileName=''):
    if FILE_UPLOAD_STORAGE.lower() != 's3':
        return UploadFileLocalSystem(tenantId, directory, uploadFile, fileName)

    file_path = ''
    try:
        if not S3_BUCKET_NAME:
            raise ValueError('S3_BUCKET_NAME is not configured')

        file_name = _build_file_name(uploadFile, fileName)
        file_path = _build_storage_key(tenantId, directory, file_name)
        content_type = mimetypes.guess_type(uploadFile.name)[0] or 'application/octet-stream'

        if hasattr(uploadFile, 'seek'):
            uploadFile.seek(0)

        _s3_client().upload_fileobj(
            uploadFile,
            S3_BUCKET_NAME,
            file_path,
            ExtraArgs={'ContentType': content_type},
        )
        return file_path
    except Exception as e:
        print("S3 Upload Error:", e)
        return UploadFileLocalSystem(tenantId, directory, uploadFile, fileName)


def UploadFileS3ServerProjectDirectory(tenantId, directory, uploadFile, fileName=''):
    return UploadFileS3Server(tenantId, directory, uploadFile, fileName)


def DownloadS3DocFile(request):
    if request.method == 'POST':
        file = request.POST.get('file')
        try:
            file_name = GetFileNameFromS3Url(file)
            response = _s3_client().get_object(Bucket=S3_BUCKET_NAME, Key=file)
            content_type = response['ContentType']
            file_content = response['Body'].read()
            http_response = HttpResponse(file_content, content_type=content_type)
            http_response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            http_response['fileName'] = str(file_name.replace(" ", "_"))
            return http_response
        except ClientError as e:
            if e.response.get('Error', {}).get('Code') == 'NoSuchKey':
                return HttpResponse('File not found', status=404)
            raise
    return HttpResponse('Invalid request method', status=405)


def GetFileNameFromS3Url(fileUrl):
    s3_path = f"{S3_URL or ''}{S3_FOLDER or ''}"
    file_name = urllib.parse.urlparse(s3_path + fileUrl).path.split("/")[-1]
    return file_name


def DeleteFileFromS3(key):
    try:
        if key and not key.startswith((MEDIA_URL, '/', 'http://', 'https://')):
            _s3_client().delete_object(Bucket=S3_BUCKET_NAME, Key=key)
    except Exception as e:
        print("S3 Delete Error:", e)
