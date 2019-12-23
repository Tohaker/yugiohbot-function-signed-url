from datetime import datetime, timedelta

from flask import abort
from google.cloud import storage


def function(request):
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return '', 204, headers

    if request.method != 'POST':
        return abort(405)

    request_json = request.get_json()

    storage_client = storage.Client.from_service_account_json('signed-url.json')

    # Get a reference to the destination file in GCS
    bucket_name = request_json['bucket']
    file_name = request_json['filename']
    file = storage_client.bucket(bucket_name).blob(file_name)

    # Create a temporary upload URL
    expires_at_ms = datetime.now() + timedelta(seconds=30)
    url = file.generate_signed_url(expires_at_ms,
                                   version='v4',
                                   content_type=request_json['contentType'])

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': ['Content-Type', 'x-goog-resumable']
    }

    return {'signed_url': url}, 200, headers
