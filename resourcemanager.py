from google.cloud import resourcemanager_v3

class ResourceManager(object):
    def __init__(self, project):
        self.project = project

    def get_project_name(self):
        client = resourcemanager_v3.ProjectsClient()
        project_path = self.project_path()
        request = resourcemanager_v3.GetProjectRequest(name=project_path)
        response = client.get_project(request=request)
        return response.display_name
    
    def project_path(self):
        client = resourcemanager_v3.ProjectsClient()
        response = client.project_path(self.project)
        return response

# aa = ResourceManager('speedy-victory-336109')
# print(aa.get_project_name())