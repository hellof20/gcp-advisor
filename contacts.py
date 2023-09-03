from google.cloud import essential_contacts_v1
from loguru import logger

class Contacts(object):
    def __init__(self, project):
        self.project = project

    def list_essential_contacts(self):
        logger.debug('%s: list_essential_contacts' % self.project)          
        result = []
        try:
            client = essential_contacts_v1.EssentialContactsServiceClient()
            request = essential_contacts_v1.ListContactsRequest(parent="projects/%s"%self.project,)
            # request = essential_contacts_v1.ListContactsRequest(parent='organizations/235918811881',)
            page_result = client.list_contacts(request=request)
            for response in page_result:
                result.append(response.email)
            if len(result) == 0:
                result = ['Not Configured']
            else:
                result = []
        except Exception as e:
            logger.warning(e)
        finally:
            return result

# aa = Contacts('speedy-victory-336109')   
# print(aa.list_essential_contacts())

