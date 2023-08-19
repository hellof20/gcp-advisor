from google.cloud import storage

class GCS(object):
    def __init__(self, project):
        self.project = project
        self.storage_client = storage.Client()

    def list_buckets(self):
        buckets = self.storage_client.list_buckets()
        for bucket in buckets:
            print(bucket)

aa = GCS('speedy-victory-336109')   
print(aa.list_buckets())            