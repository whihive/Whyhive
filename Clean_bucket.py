from google.cloud import storage
from google.cloud.exceptions import NotFound
def delete_from_gcloud(bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = list(bucket.list_blobs())
    if len(blobs)>0:
        for i in range(len(blobs)):
            bucket.delete_blob(str(blobs[i]).split('.')[0].split(', ')[1]+".ogg")
