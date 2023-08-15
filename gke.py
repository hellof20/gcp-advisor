from google.cloud import container_v1

class GKE(object):
    def __init__(self, project):
        self.project = project

    def list_clusters(self):
        client = container_v1.ClusterManagerClient()
        request = container_v1.ListClustersRequest(parent="projects/%s/locations/-" % (self.project))
        result = client.list_clusters(request=request)
        return result

    def check_gke_controller_regional(self):
        result = []
        response = self.list_clusters()
        for cluster in response.clusters:
            if len(cluster.location.split('-')) != 2:
                result.append(cluster.name)
        return result
        
    def check_gke_static_version(self):
        result = []
        response = self.list_clusters()
        for cluster in response.clusters:
            if cluster.release_channel.channel.name != 'UNSPECIFIED':
                result.append(cluster.name)
        return result

    def check_gke_nodepool_upgrade(self):
        result = []
        response = self.list_clusters()
        for cluster in response.clusters:
            for pool in cluster.node_pools:
                if pool.management.auto_upgrade == True:
                    result.append(cluster.name + ':' + pool.name)
        return result        

# gke = GKE('speedy-victory-336109')
# gke.check_gke_static_version()