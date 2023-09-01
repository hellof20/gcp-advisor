from google.cloud import essential_contacts_v1
from resourcemanager import ResourceManager
from loguru import logger

class Contacts(object):
    def __init__(self, project):
        self.project = project

    def list_essential_contacts(self):
        try:
            result = []
            client = essential_contacts_v1.EssentialContactsServiceClient()
            request = essential_contacts_v1.ListContactsRequest(parent="projects/%s"%self.project,)
            resourcemanager = ResourceManager(self.project)
            project_name = resourcemanager.get_project_name()
            # request = essential_contacts_v1.ListContactsRequest(parent='organizations/235918811881',)
            page_result = client.list_contacts(request=request)
            for response in page_result:
                result.append(response.email)
            if len(result) == 0:
                return(['Not Configured'])
        except Exception as e:
            logger.warning(e)
            pass

# aa = Contacts('speedy-victory-336109')   
# print(aa.list_essential_contacts())

