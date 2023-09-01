from google.cloud import redis_v1
from loguru import logger

class Redis(object):
    def __init__(self, project):
        self.project = project
        self.instances = self.list_all_redis_instances()

    def list_all_redis_instances(self):
        logger.debug('%s: list_all_redis_instances' % self.project)            
        result = []
        try:        
            client = redis_v1.CloudRedisClient()
            request = redis_v1.ListInstancesRequest(parent="projects/%s/locations/-" % (self.project))
            page_result = client.list_instances(request=request)
            for response in page_result:
                result.append(response)
        except Exception as e:
            logger.warning(e)
        finally:
            return result

    def check_redis_maintain_window(self):
        logger.debug('%s: check_redis_maintain_window' % self.project)            
        result = []        
        try:
            for instance in self.instances:
                if not instance.maintenance_policy:
                    result.append(instance.name.split('/')[-1])
            return result
        except Exception as e:
            logger.warning(e)
        finally:
            return result

    def check_redis_ha(self):
        logger.debug('%s: check_redis_ha' % self.project)            
        result = []          
        try:
            for instance in self.instances:
                if instance.tier.name == 'BASIC':
                    result.append(instance.name.split('/')[-1])
        except Exception as e:
            logger.warning(e)
        finally:
            return result

    def check_redis_rdb(self):
        logger.debug('%s: check_redis_rdb' % self.project)            
        result = []        
        try:
            for instance in self.instances:
                if instance.persistence_config.persistence_mode.name == 'DISABLED':
                    result.append(instance.name.split('/')[-1])
        except Exception as e:
            logger.warning(e)
        finally:
            return result

# aa = Redis('speedy-victory-336109')
# print(aa.check_redis_maintain_window())
# print(aa.check_redis_ha())
# print(aa.check_redis_rdb())