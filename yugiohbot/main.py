from datetime import datetime, timedelta

from flask import abort
from google.cloud import storage


def function(request):
    if request.method != 'POST':
        return abort(405)

    request_json = request.get_json()

    storage_client = storage.Client()

    # Get a reference to the destination file in GCS
    bucket_name = request_json['bucket']
    file_name = request_json['filename']
    file = storage_client.bucket(bucket_name).blob(file_name)

    # Create a temporary upload URL
    expires_at_ms = datetime.now() + timedelta(seconds=30)
    url = file.generate_signed_url(expires_at_ms,
                                   version='v4',
                                   content_type=request_json['contentType'])

    return url
