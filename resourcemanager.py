from google.cloud import resourcemanager_v3
from loguru import logger

class ResourceManager(object):
    def __init__(self, project):
        self.project = project

    def get_project_name(self):
        try:
            client = resourcemanager_v3.ProjectsClient()
            project_path = self.project_path()
            request = resourcemanager_v3.GetProjectRequest(name=project_path)
            response = client.get_project(request=request)
            return response.display_name
        except Exception as e:
            logger.warning(e)
            pass
    
    def project_path(self):
        try:
            client = resourcemanager_v3.ProjectsClient()
            response = client.project_path(self.project)
            return response
        except Exception as e:
            logger.warning(e)
            pass

# aa = ResourceManager('speedy-victory-336109')
# print(aa.get_project_name())