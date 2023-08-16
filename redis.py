from google.cloud import redis_v1
from compute import Compute

class Redis(object):
    def __init__(self, project):
        self.project = project
        self.instances = self.list_all_instances()

    def list_all_instances(self):
        try:        
            result = []
            client = redis_v1.CloudRedisClient()
            request = redis_v1.ListInstancesRequest(parent="projects/%s/locations/-" % (self.project))
            page_result = client.list_instances(request=request)
            for response in page_result:
                result.append(response)
            return result
        except:
            pass           

    def check_redis_maintain_window(self):
        try:
            result = []
            for instance in self.instances:
                if not instance.maintenance_policy:
                    result.append(instance.name.split('/')[-1])
            return result
        except:
            pass

    def check_redis_ha(self):
        try:
            result = []
            for instance in self.instances:
                if instance.tier.name == 'BASIC':
                    result.append(instance.name.split('/')[-1])
            return result
        except:
            pass       

    def check_redis_rdb(self):
        try:
            result = []
            for instance in self.instances:
                if instance.persistence_config.persistence_mode.name == 'DISABLED':
                    result.append(instance.name.split('/')[-1])
            return result
        except:
            pass

# aa = Redis('speedy-victory-336109')
# print(aa.check_redis_maintain_window())
# print(aa.check_redis_ha())
# print(aa.check_redis_rdb())