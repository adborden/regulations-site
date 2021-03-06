from __future__ import absolute_import

import os
import shutil
import tempfile
import contextlib

import boto3
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from celery import shared_task
from django.conf import settings


@shared_task
def submit_comment(comment):
    with TemporaryDirectory() as path:
        fields = [
            ("comment_on", comment["document_id"]),
            ("general_comment", comment["comment"]),
        ]
        files = [('uploadedFile', (
            file['name'], fetch_file(path, file['key'], file['name']))
            )
            for file in comment.get('files', [])
        ]
        fields.extend(files)
        data = MultipartEncoder(fields)
        response = requests.post(
            settings.REGS_API_URL,
            data=data,
            headers={
                "Content-Type": data.content_type,
                "X-Api-Key": settings.REGS_API_KEY
            }
        )
        print(response.text)


@contextlib.contextmanager
def TemporaryDirectory(*args, **kwargs):
    try:
        path = tempfile.mkdtemp(*args, **kwargs)
        yield path
    finally:
        shutil.rmtree(path)


def fetch_file(path, key, name):
    session = boto3.Session(
        aws_access_key_id=settings.ACCESS_KEY_ID,
        aws_secret_access_key=settings.SECRET_ACCESS_KEY,
    )
    s3 = session.client('s3')
    dest = os.path.join(path, name)
    s3.download_file(settings.BUCKET, key, dest)
    return dest
