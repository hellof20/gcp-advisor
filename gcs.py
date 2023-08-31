from google.cloud import storage

class GCS(object):
    def __init__(self, project):
        self.project = project
        self.storage_client = storage.Client()
        self.buckets = self.list_buckets()

    def list_buckets(self):
        try:
            result = []
            buckets = self.storage_client.list_buckets()
            for bucket in buckets:
                result.append(bucket)
            return result
        except:
            pass        

    def list_public_buckets(self):
        try:
            result = []
            for bucket in self.buckets:
                bindings = bucket.get_iam_policy().bindings
                # print(bindings)
                for i in bindings:
                    for member in i['members']:
                        if member == 'allUsers':
                            result.append(bucket.name)
            return result
        except:
            pass            

# aa = GCS('speedy-victory-336109')   
# print(aa.list_public_buckets())            