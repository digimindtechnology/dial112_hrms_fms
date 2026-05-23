import mimetypes
import os
import urllib.parse
from datetime import datetime
from pathlib import Path
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.http import HttpResponse
from DmtHrmsFmsApp.settings import (AWS_S3_ENDPOINT_URL, AWS_S3_REGION_NAME, FILE_UPLOAD_STORAGE, IS_FILE_UPLOAD_S3, MEDIA_ROOT, MEDIA_URL, S3_BUCKET_NAME, S3_FOLDER, S3_URL, aws_access_key_id, aws_secret_access_key, )


# =========================================================
# COMMON
# =========================================================

def UploadFileData(tenantId, directory, uploadFile, fileName=''):
    if IS_FILE_UPLOAD_S3:
        return UploadFileS3Server(tenantId, directory, uploadFile, fileName)
    return UploadFileLocalSystem(tenantId, directory, uploadFile, fileName)


# =========================================================
# LOCAL STORAGE
# =========================================================
def UploadFileLocalSystem(tenantId, directory, uploadFile, fileName=''):
    try:
        file_name = _build_file_name(uploadFile, fileName)
        directory = directory.strip('/\\')
        # Physical storage path
        directory_path = os.path.join(MEDIA_ROOT, 'company_doc', str(tenantId), directory)
        os.makedirs(directory_path, exist_ok=True)
        # Full physical file path
        save_path = os.path.join(directory_path, file_name)

        # Reset pointer
        if hasattr(uploadFile, 'seek'):
            uploadFile.seek(0)

        # Save file physically
        with open(save_path, 'wb+') as destination:
            # Django UploadedFile
            if hasattr(uploadFile, 'chunks'):
                for chunk in uploadFile.chunks():
                    destination.write(chunk)
            # Normal file object
            else:
                destination.write(uploadFile.read())
        return os.path.join('company_doc', str(tenantId), directory, file_name).replace('\\', '/')
    except Exception as e:
        print("Local Upload Error:", str(e))
        return ''


# =========================================================
# S3 STORAGE
# =========================================================
def UploadFileS3Server(tenantId, directory, uploadFile, fileName=''):
    if FILE_UPLOAD_STORAGE.lower() != 's3':
        return UploadFileLocalSystem(
            tenantId,
            directory,
            uploadFile,
            fileName
        )

    try:

        if not S3_BUCKET_NAME:
            raise ValueError("S3_BUCKET_NAME is missing")

        file_name = _build_file_name(uploadFile, fileName)

        file_key = _build_storage_key(
            tenantId,
            directory,
            file_name
        )

        content_type = (
                mimetypes.guess_type(uploadFile.name)[0]
                or 'application/octet-stream'
        )

        if hasattr(uploadFile, 'seek'):
            uploadFile.seek(0)

        _s3_client().upload_fileobj(
            uploadFile,
            S3_BUCKET_NAME,
            file_key,
            ExtraArgs={
                'ContentType': content_type
            }
        )

        return file_key

    except Exception as e:

        print("S3 Upload Error:", str(e))

        return UploadFileLocalSystem(
            tenantId,
            directory,
            uploadFile,
            fileName
        )


# =========================================================
# S3 CONFIG
# =========================================================

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


def _s3_client():
    return boto3.client('s3', **_s3_kwargs())


def _s3_resource():
    return boto3.resource('s3', **_s3_kwargs())


def _storage_prefix():
    return (S3_FOLDER or '').strip('/')


def _build_storage_key(tenantId, directory, file_name):
    parts = [
        _storage_prefix(),
        str(tenantId),
        directory.strip('/'),
        file_name
    ]

    return '/'.join(part for part in parts if part)


def _build_file_name(upload_file, file_name=''):
    """
    Generate unique file name.
    """
    original_extension = Path(upload_file.name).suffix

    if file_name:
        base_name = Path(file_name).stem
    else:
        base_name = Path(upload_file.name).stem

    base_name = base_name.replace(' ', '_')

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')

    return f"{timestamp}_{base_name}{original_extension}"


# =========================================================
# DOWNLOAD
# =========================================================

def DownloadS3DocFile(request):
    if request.method != 'POST':
        return HttpResponse(
            'Invalid request method',
            status=405
        )

    file_key = request.POST.get('file')

    if not file_key:
        return HttpResponse(
            'File key missing',
            status=400
        )

    try:

        response = _s3_client().get_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_key
        )

        file_content = response['Body'].read()

        content_type = response.get(
            'ContentType',
            'application/octet-stream'
        )

        file_name = GetFileNameFromS3Url(file_key)

        http_response = HttpResponse(
            file_content,
            content_type=content_type
        )

        http_response[
            'Content-Disposition'
        ] = f'attachment; filename="{file_name}"'

        return http_response

    except ClientError as e:

        error_code = e.response.get(
            'Error',
            {}
        ).get('Code')

        if error_code == 'NoSuchKey':
            return HttpResponse(
                'File not found',
                status=404
            )

        print("S3 Download Error:", str(e))

        return HttpResponse(
            'Download failed',
            status=500
        )


# =========================================================
# FILE HELPERS
# =========================================================

def GetFileNameFromS3Url(fileUrl):
    parsed_url = urllib.parse.urlparse(fileUrl)
    return os.path.basename(parsed_url.path)
def DeleteFileFromS3(key):
    try:
        if not key:
            return

        if key.startswith((
                MEDIA_URL,
                '/',
                'http://',
                'https://'
        )):
            return

        _s3_client().delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=key
        )

    except Exception as e:
        print("S3 Delete Error:", str(e))


# =========================================================
# DIRECTORY MANAGEMENT
# =========================================================

class S3DirectoryManager:
    @staticmethod
    def create(directory_name):
        directory_name = directory_name.rstrip('/') + '/'
        _s3_resource().Bucket(
            S3_BUCKET_NAME
        ).put_object(Key=directory_name)
        return directory_name

    @staticmethod
    def rename(old_directory, new_directory):
        bucket = S3_BUCKET_NAME
        old_directory = old_directory.rstrip('/') + '/'
        new_directory = new_directory.rstrip('/') + '/'
        client = _s3_client()
        response = client.list_objects_v2(
            Bucket=bucket,
            Prefix=old_directory
        )

        if 'Contents' in response:
            for obj in response['Contents']:
                old_key = obj['Key']
                new_key = old_key.replace(
                    old_directory,
                    new_directory,
                    1
                )
                client.copy_object(
                    Bucket=bucket,
                    CopySource={
                        'Bucket': bucket,
                        'Key': old_key
                    },
                    Key=new_key
                )
                client.delete_object(
                    Bucket=bucket,
                    Key=old_key
                )
        return new_directory

    @staticmethod
    def delete(directory_name):
        bucket = S3_BUCKET_NAME
        directory_name = directory_name.rstrip('/') + '/'
        client = _s3_client()
        response = client.list_objects_v2(
            Bucket=bucket,
            Prefix=directory_name
        )
        if 'Contents' in response:
            for obj in response['Contents']:
                client.delete_object(
                    Bucket=bucket,
                    Key=obj['Key']
                )
        return directory_name


# =========================================================
# FILE URL
# =========================================================

def GetFileUrl(file_path):
    if not file_path:
        return ''
    filePath = S3_URL if IS_FILE_UPLOAD_S3 else f"{MEDIA_URL}"
    if file_path.startswith(('http://', 'https://', filePath, '/')):
        return file_path
    base_url = (filePath or '').rstrip('/')
    return f"{base_url}/{file_path}"
