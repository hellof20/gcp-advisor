from google.cloud import recommender_v1
from compute import Compute
from sql import SQL

class Recommender(object):
    def __init__(self, project):
        self.project = project
        self.client = recommender_v1.RecommenderClient()
        self.compute = Compute(self.project)
        self.vm_zones = self.compute.list_all_instances_zones()
        self.sql = SQL(self.project)
        self.sql_instances = self.sql.list_sql_instances()


    def recommender_idle_vm(self):
        try:
            result = []
            for zone in self.vm_zones:
                parent = 'projects/%s/locations/%s/recommenders/%s' %(self.project, zone, 'google.compute.instance.IdleResourceRecommender')
                request = recommender_v1.ListRecommendationsRequest(parent=parent)
                page_result = self.client.list_recommendations(request=request)
                for response in page_result:
                    vm_name = response.content.overview['resource'].split('/')[-1]
                    result.append(vm_name)
            return result
        except:
            pass         


    def recommender_idle_sql(self):
        try:        
            result = []
            for instance in self.sql_instances:
                region = instance['region']
                parent = 'projects/%s/locations/%s/recommenders/%s' %(self.project, region, 'google.cloudsql.instance.IdleRecommender')
                request = recommender_v1.ListRecommendationsRequest(parent=parent)
                page_result = self.client.list_recommendations(request=request)
                for response in page_result:
                    result.append(response.content.overview['resource'])
            return result
        except:
            pass

# aa = Recommender('pangu-358004')   
# print(aa.recommender_idle_sql())

# https://cloud.google.com/recommender/docs/recommenders
# https://cloud.google.com/sql/docs/mysql/recommender-sql-idle