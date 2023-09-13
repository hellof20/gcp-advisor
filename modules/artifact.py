import googleapiclient.discovery as discovery
from loguru import logger

class Registry(object):
    def __init__(self, project):
        self.project = project
        self.registry = discovery.build('artifactregistry', 'v1')
        self.locations = self.list_artifact_registry_locations()
        self.repos = self.list_artifact_registry_repos()


    def list_artifact_registry_locations(self):
        logger.debug('%s: list_artifact_registry_locations' % self.project)
        result = []
        try:
            req = self.registry.projects().locations().list(name="projects/%s" % self.project)
            resp = req.execute()
            for location in resp['locations']:
                result.append(location['locationId'])
        except Exception as e:
            logger.warning(e)
        finally:
            return result
    
    def list_artifact_registry_repos(self):
        logger.debug('%s: list_artifact_registry_repos' % self.project)
        result = []
        try:
            for location in self.locations:
                req = self.registry.projects().locations().repositories().list(parent="projects/%s/locations/%s" % (self.project, location))
                resp = req.execute()
                if 'repositories' in resp:
                    for repo in resp['repositories']:
                        if 'name' in repo:
                            result.append(repo['name'])
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def check_artifact_registry_redirection(self):
        logger.debug('%s: check_artifact_registry_redirection' % self.project)   
        result = []
        redirection = ''
        use_container = 'no'
        try:
            req = self.registry.projects().getProjectSettings(name="projects/%s/projectSettings" % self.project)
            resp = req.execute()
            if 'legacyRedirectionState' in resp:
                if resp['legacyRedirectionState'] == 'REDIRECTION_FROM_GCR_IO_DISABLED':
                    redirection = 'disabled'
                else:
                    redirection = 'enabled'
            repos = []
            for repo in self.repos:
                repos.append(repo.split('/')[-1])
            for i in ['asia.gcr.io','us.gcr.io','gcr.io','eu.gcr.io']:
                if i in repos:
                    use_container = 'yes'
            if redirection == 'disabled' and use_container == 'yes':
                result.append('Need Migrate')
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def list_artifact_registry_dockerimages(self):
        logger.debug('%s: list_artifact_registry_dockerimages' % self.project)
        result = []
        try:
            for repo in self.repos:
                req = self.registry.projects().locations().repositories().dockerImages().list(parent=repo)
                resp = req.execute()
                if 'dockerImages' in resp:
                    result.append(resp['dockerImages'])
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def list_no_tag_docker_images(self):
        logger.debug('%s: list_no_tag_docker_images' % self.project)
        result = []
        imagelist = []
        dict = {}
        try:
            dockerimages = self.list_artifact_registry_dockerimages()
            for images in dockerimages:
                for image in images:
                    if 'tags' not in image:
                        image_name = image['name'].split('@')[0]
                        imagelist.append(image_name)
            for i in imagelist:
                if i in dict:
                    dict[i] += 1
                else:
                    dict[i] = 1
            result = list(dict.items())
        except Exception as e:
            logger.warning(e)
        finally:
            return result                


# aa = Registry('speedy-victory-336109')
# print(aa.list_no_tag_docker_images())