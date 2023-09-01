import googleapiclient.discovery as discovery
from loguru import logger

class SQL(object):
    def __init__(self, project):
        self.project = project
        self.sqladmin = discovery.build('sqladmin', 'v1')
        self.instances = self.list_sql_instances()


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
                    logger.debug("%s: %s" %(instance['name'],instance['settings']['maintenanceWindow']))
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
                if 'secondaryZone' not in instance['settings']['locationPreference']:
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
                if not instance['settings']['deletionProtectionEnabled']:
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

# aa = SQL('aethergazeren')   
# instances = aa.check_sql_maintenance()
# print(instances)
# for instance in instances:
#     print(instance['region'])