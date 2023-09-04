import googleapiclient.discovery as discovery
from loguru import logger


class Logging(object):
    def __init__(self, project):
        self.project = project
        self.log = discovery.build('logging', 'v2')
        self.buckets = self.list_log_bucket()
    
    def list_log_bucket(self):
        logger.debug('%s: list_log_bucket' % self.project)          
        result = []
        try:
            req = self.log.projects().locations().buckets().list(parent='projects/%s/locations/-' % self.project)
            resp = req.execute()
            result = resp['buckets']
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def check_if_analytics_enabled(self):
        logger.debug('%s: check_if_analytics_enabled' % self.project)          
        result = []        
        try:        
            num = 0
            for bucket in self.buckets:
                if 'analyticsEnabled' in bucket:
                    if bucket['analyticsEnabled'] == True:
                        num += 1
            if num == 0:
                result.append("Not Enabled")
        except Exception as e:
            logger.warning(e)
        finally:
            return result


# aa = Logging('speedy-victory-336109')   
# print(aa.check_if_analytics_enabled())