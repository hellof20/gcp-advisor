from google.cloud import storage
from loguru import logger

class GCS(object):
    def __init__(self, project):
        self.project = project
        self.storage_client = storage.Client()
        self.buckets = self.list_buckets()

    def list_buckets(self):
        logger.debug('%s: list_buckets' % self.project)   
        result = []               
        try:
            buckets = self.storage_client.list_buckets(
                project = self.project
            )
            for bucket in buckets:
                result.append(bucket)
        except Exception as e:
            logger.warning(e)
        finally:
            return result       

    def list_public_buckets(self):
        logger.debug('%s: list_public_buckets' % self.project)   
        result = []             
        try:
            for bucket in self.buckets:
                bindings = bucket.get_iam_policy().bindings
                for i in bindings:
                    for member in i['members']:
                        if member == 'allUsers':
                            result.append(bucket.name)
        except Exception as e:
            logger.warning(e)
        finally:
            return result          

# aa = GCS('speedy-victory-336109')   
# print(aa.list_public_buckets())            