from google.cloud import container_v1
from loguru import logger

class GKE(object):
    def __init__(self, project):
        self.project = project
        self.client = container_v1.ClusterManagerClient()
        self.result = self.list_clusters()

    def list_clusters(self):
        logger.debug('%s: list_clusters' % self.project)        
        result = []
        try:
            request = container_v1.ListClustersRequest(parent="projects/%s/locations/-" % (self.project))
            result = self.client.list_clusters(request=request)
        except Exception as e:
            logger.warning(e)
        finally:
            return result           

    def check_gke_controller_regional(self):
        logger.debug('%s: check_gke_controller_regional' % self.project)        
        result = []
        try:        
            for cluster in self.result.clusters:
                if len(cluster.location.split('-')) != 2:
                    result.append(cluster.name)
        except Exception as e:
            logger.warning(e)
        finally:
            return result      
        
    def check_gke_static_version(self):
        logger.debug('%s: check_gke_static_version' % self.project)        
        result = []
        try:        
            for cluster in self.result.clusters:
                if cluster.release_channel.channel.name != 'UNSPECIFIED':
                    result.append(cluster.name)
        except Exception as e:
            logger.warning(e)
        finally:
            return result 

    def check_gke_nodepool_upgrade(self):
        logger.debug('%s: check_gke_nodepool_upgrade' % self.project)        
        result = []
        try:        
            for cluster in self.result.clusters:
                for pool in cluster.node_pools:
                    if pool.management.auto_upgrade == True:
                        result.append(cluster.name + ':' + pool.name)      
        except Exception as e:
            logger.warning(e)
        finally:
            return result    


    def check_gke_public_cluster(self): 
        logger.debug('%s: check_gke_public_cluster' % self.project)           
        result = []        
        try:   
            for cluster in self.result.clusters:
                for pool in cluster.node_pools:
                    if pool.network_config.enable_private_nodes == False:
                        result.append(cluster.name)
            result = list(set(result))
        except Exception as e:
            logger.warning(e)
        finally:
            return result

# gke = GKE('speedy-victory-336109')
# print(gke.check_gke_public_cluster())