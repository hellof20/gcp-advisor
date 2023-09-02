from google.cloud import recommender_v1
from compute import Compute
from sql import SQL
from loguru import logger

class Recommender(object):
    def __init__(self, project):
        self.project = project
        self.client = recommender_v1.RecommenderClient()
        self.compute = Compute(self.project)
        self.vm_zones = self.compute.list_all_instances_zones()
        self.sql = SQL(self.project)


    def recommender_idle_vm(self):
        logger.debug('%s: recommender_idle_vm' % self.project)          
        result = []        
        try:
            for zone in self.vm_zones:
                parent = 'projects/%s/locations/%s/recommenders/%s' %(self.project, zone, 'google.compute.instance.IdleResourceRecommender')
                request = recommender_v1.ListRecommendationsRequest(parent=parent)
                page_result = self.client.list_recommendations(request=request)
                for response in page_result:
                    vm_name = response.content.overview['resource'].split('/')[-1]
                    result.append(vm_name)
        except Exception as e:
            logger.warning(e)
        finally:
            return result 


    def recommender_idle_sql(self):
        logger.debug('%s: recommender_idle_sql' % self.project)            
        result = []
        try:        
            for instance in self.sql.instances:
                region = instance['region']
                parent = 'projects/%s/locations/%s/recommenders/%s' %(self.project, region, 'google.cloudsql.instance.IdleRecommender')
                request = recommender_v1.ListRecommendationsRequest(parent=parent)
                page_result = self.client.list_recommendations(request=request)
                for response in page_result:
                    result.append(response.content.overview['resource'])
        except Exception as e:
            logger.warning(e)
        finally:
            return result 

# aa = Recommender('aethergazeren')   
# print(aa.recommender_idle_vm())

# https://cloud.google.com/recommender/docs/recommenders
# https://cloud.google.com/sql/docs/mysql/recommender-sql-idle