from google.cloud import redis_v1
from compute import Compute

class Redis(object):
    def __init__(self, project):
        self.project = project

    def list_all_instances(self):
        result = []
        client = redis_v1.CloudRedisClient()
        request = redis_v1.ListInstancesRequest(parent="projects/%s/locations/-" % (self.project))
        page_result = client.list_instances(request=request)
        for response in page_result:
            result.append(response)
        return result

    def check_redis_maintain_window(self):
        redis_instances = self.list_all_instances()
        result = []
        for instance in redis_instances:
            if not instance.maintenance_policy:
                result.append(instance.name.split('/')[-1])
        return result

    def check_redis_ha(self):
        redis_instances = self.list_all_instances()
        result = []
        for instance in redis_instances:
            if instance.tier.name == 'BASIC':
                result.append(instance.name.split('/')[-1])
        return result

    def check_redis_rdb(self):
        redis_instances = self.list_all_instances()
        result = []
        for instance in redis_instances:
            if instance.persistence_config.persistence_mode.name == 'DISABLED':
                result.append(instance.name.split('/')[-1])
        return result

# aa = Redis('speedy-victory-336109')
# result = aa.list_all_instances()
# print(check_redis_maintain_window(result))
# print('---------------')
# print(check_redis_ha(result))
# print('---------------')
# print(check_redis_rdb(result))