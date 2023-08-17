import googleapiclient.discovery as discovery

class SQL(object):
    def __init__(self, project):
        self.project = project
        self.sqladmin = discovery.build('sqladmin', 'v1')
        self.instances = self.list_sql_instances()


    def list_sql_instances(self):
        try:
            req = self.sqladmin.instances().list(project=self.project)
            resp = req.execute()
            return resp['items']
        except:
            pass


    def check_sql_maintenance(self):
        try:
            result = []
            for instance in self.instances:
                hour = instance['settings']['maintenanceWindow']['hour']
                day = instance['settings']['maintenanceWindow']['day']
                if hour == 0 and day == 0:
                    result.append(instance['name'])
            return result
        except:
            pass


    def check_sql_ha(self):
        try:
            result = []
            for instance in self.instances:
                if 'secondaryZone' not in instance['settings']['locationPreference']:
                    result.append(instance['name'])
            return result
        except:
            pass     


    def check_sql_query_insight(self):
        try:
            result = []
            for instance in self.instances:
                if 'queryInsightsEnabled' not in instance['settings']['insightsConfig']:
                    result.append(instance['name'])
            return result
        except:
            pass


    def check_sql_delete_protect(self):
        try:
            result = []
            for instance in self.instances:
                if not instance['settings']['deletionProtectionEnabled']:
                    result.append(instance['name'])
            return result
        except:
            pass


    def check_sql_public_access(self):
        try:
            result = []
            for instance in self.instances:
                for x in instance['ipAddresses']:
                    if x['type'] == 'PRIMARY':
                        result.append(instance['name'])
            return result
        except:
            pass

# aa = SQL('pangu-358004')   
# instances = aa.list_sql_instances()
# for instance in instances:
#     print(instance['region'])