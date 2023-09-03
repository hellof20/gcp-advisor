import googleapiclient.discovery as discovery
from google.cloud import recommender_v1
from loguru import logger

class SQL(object):
    def __init__(self, project):
        self.project = project
        self.sqladmin = discovery.build('sqladmin', 'v1')
        self.instances = self.list_sql_instances()
        self.recommender_client = recommender_v1.RecommenderClient()


    def list_sql_instances(self):
        logger.debug('%s: list_sql_instances' % self.project)
        result = []
        try:
            req = self.sqladmin.instances().list(project=self.project)
            resp = req.execute()
            if 'items' in resp:
                result = resp['items']
        except Exception as e:
            logger.warning(e)
        finally:
            return result   


    def check_sql_maintenance(self):
        logger.debug('%s: check_sql_maintenance' % self.project)        
        result = []
        try:
            for instance in self.instances:
                if 'maintenanceWindow' in instance['settings']:
                    # logger.debug("%s: %s" %(instance['name'],instance['settings']['maintenanceWindow']))
                    hour = instance['settings']['maintenanceWindow']['hour']
                    day = instance['settings']['maintenanceWindow']['day']
                    if hour == 0 and day == 0:
                        result.append(instance['name'])
        except Exception as e:
            logger.warning(e)
        finally:
            return result  


    def check_sql_ha(self):
        logger.debug('%s: check_sql_ha' % self.project)        
        result = []
        try:
            for instance in self.instances:
                if instance['settings']['availabilityType'] == 'ZONAL' and instance['instanceType'] != 'READ_REPLICA_INSTANCE':
                    result.append(instance['name'])
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def check_sql_slow_query(self):
        logger.debug('%s: check_sql_slow_query' % self.project)        
        result = []
        flag_dict = {}
        try:
            for instance in self.instances:
                if 'databaseFlags' in instance['settings']:                
                    for flag in instance['settings']['databaseFlags']:
                        flag_dict[flag['name']] = flag['value']
                else:
                    result.append(instance['name'])
                if 'slow_query_log' not in flag_dict:
                    result.append(instance['name'])
                if 'slow_query_log' in flag_dict and flag_dict['slow_query_log'] == 'off':
                    result.append(instance['name'])
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def check_sql_query_insight(self):
        logger.debug('%s: check_sql_query_insight' % self.project)        
        result = []
        try:
            for instance in self.instances:
                if 'insightsConfig' not in instance['settings']:
                    result.append(instance['name'])
                else:
                    if 'queryInsightsEnabled' not in instance['settings']['insightsConfig']:
                        result.append(instance['name'])
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def check_sql_delete_protect(self):
        logger.debug('%s: check_sql_delete_protect' % self.project)        
        result = []
        try:
            for instance in self.instances:
                if 'deletionProtectionEnabled' not in instance['settings']:
                    result.append(instance['name'])
                else:
                    if instance['settings']['deletionProtectionEnabled'] == False:
                        result.append(instance['name'])
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def check_sql_public_access(self):
        logger.debug('%s: check_sql_public_access' % self.project)        
        result = []        
        try:
            for instance in self.instances:
                for net in instance['settings']['ipConfiguration']['authorizedNetworks']:
                    if net['value'] == '0.0.0.0/0':
                        result.append(instance['name'])
                # for x in instance['ipAddresses']:
                #     if x['type'] == 'PRIMARY':
                #         result.append(instance['name'])
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def check_sql_storage_auto_resize(self):
        logger.debug('%s: check_sql_storage_auto_resize' % self.project)        
        result = []        
        try:
            for instance in self.instances:
                if instance['settings']['storageAutoResize'] != True:
                    result.append(instance['name'])
            return result
        except Exception as e:
            logger.warning(e)
        finally:
            return result    


    def recommender_idle_sql(self):
        logger.debug('%s: recommender_idle_sql' % self.project)            
        result = []
        try:        
            for instance in self.instances:
                region = instance['region']
                parent = 'projects/%s/locations/%s/recommenders/%s' %(self.project, region, 'google.cloudsql.instance.IdleRecommender')
                request = recommender_v1.ListRecommendationsRequest(parent=parent)
                page_result = self.recommender_client.list_recommendations(request=request)
                for response in page_result:
                    result.append(response.content.overview['resource'])
        except Exception as e:
            logger.warning(e)
        finally:
            return result                     

# aa = SQL('farlight-hadoop')   
# print(aa.check_sql_delete_protect())
# for instance in instances:
#     print(instance['region'])