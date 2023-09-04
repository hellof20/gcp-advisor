from google.cloud import resourcemanager_v3
from loguru import logger

class ResourceManager(object):
    def __init__(self, project):
        self.project = project

    def get_project_name(self):
        logger.debug('%s: get_project_name' % self.project)        
        result = []
        try:
            client = resourcemanager_v3.ProjectsClient()
            project_path = self.project_path()
            request = resourcemanager_v3.GetProjectRequest(name=project_path)
            response = client.get_project(request=request)
            result = response.display_name
        except Exception as e:
            logger.warning(e)
        finally:
            return result 
    
    def project_path(self):
        logger.debug('%s: project_path' % self.project)        
        result = []
        try:
            client = resourcemanager_v3.ProjectsClient()
            response = client.project_path(self.project)
            result = response
        except Exception as e:
            logger.warning(e)
        finally:
            return result 

# aa = ResourceManager('aethergazeren')
# print(aa.get_project_name())