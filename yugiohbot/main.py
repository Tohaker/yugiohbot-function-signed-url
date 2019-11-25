from datetime import datetime, timedelta

from flask import abort
from google.auth import compute_engine, default
from google.auth.transport import requests
from google.cloud import storage


def function(request):
    if request.method != 'POST':
        return abort(405)

    request_json = request.get_json()

    # Allows us to generate without providing a service account file.
    auth_request = requests.Request()
    credentials, project = default()
    storage_client = storage.Client(project, credentials)

    # Get a reference to the destination file in GCS
    bucket_name = request_json['bucket']
    file_name = request_json['filename']
    file = storage_client.bucket(bucket_name).blob(file_name)

    signing_credentials = compute_engine.IDTokenCredentials(auth_request, "",
                                                            service_account_email=credentials.service_account_email)

    # Create a temporary upload URL
    expires_at_ms = datetime.now() + timedelta(seconds=30)
    url = file.generate_signed_url(expires_at_ms,
                                   credentials=signing_credentials,
                                   version='v4',
                                   content_type=request_json['contentType'])

    return url
