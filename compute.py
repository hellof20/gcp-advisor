from google.cloud import compute_v1
from resourcemanager import ResourceManager

class Compute(object):
    def __init__(self, project):
        self.project = project
        self.all_instances = self.list_all_instances()

    def list_all_instances(self):
        try:
            result = []
            instance_client = compute_v1.InstancesClient()
            request = {"project" : self.project}
            agg_list = instance_client.aggregated_list(request=request)
            for zone, response in agg_list:
                if response.instances:
                    for instance in response.instances:
                        result.append(instance)
            return result
        except:
            pass


    def list_all_instances_zones(self):
        try:
            result = []
            instance_client = compute_v1.InstancesClient()
            request = {"project" : self.project}
            agg_list = instance_client.aggregated_list(request=request)
            for zone, response in agg_list:
                if response.instances:
                        result.append(zone.split('/')[-1])
            return result
        except:
            pass        


    def list_idle_ips(self):
        try:
            result = []
            address_client = compute_v1.AddressesClient()
            request = compute_v1.AggregatedListAddressesRequest(project=self.project)
            page_result = address_client.aggregated_list(request=request)
            for region,response in page_result:
                if response.addresses:
                    for address in response.addresses:
                        if address.status == 'RESERVED' and address.address_type == 'EXTERNAL':
                            result.append(address.address)
            return result
        except:
            pass


    def list_idle_disks(self):
        try:
            result = []
            disk_client = compute_v1.DisksClient()
            request = compute_v1.AggregatedListDisksRequest(project=self.project)
            page_result = disk_client.aggregated_list(request=request)
            for zone,response in page_result:
                if response.disks:
                    for disk in response.disks:
                        if not disk.users:
                            result.append(disk.name)
            return result
        except:
            pass        


    def list_all_regions(self):
        try:
            result = []
            client = compute_v1.RegionsClient()
            request = compute_v1.ListRegionsRequest(project=self.project)
            page_result = client.list(request=request)
            for response in page_result:
                result.append(response.name)
            return result
        except:
            pass


    def list_no_snapshots_project(self):
        try:
            result = []
            client = compute_v1.SnapshotsClient()
            request = compute_v1.ListSnapshotsRequest(project=self.project)
            page_result = client.list(request=request)
            for response in page_result:
                result.append(response.name)
            if len(result) == 0:
                return [self.project]
            else:
                pass
        except:
            pass


    def list_no_deletion_protection(self):
        result = []
        result_num = 0
        resourcemanager = ResourceManager(self.project)
        project_name = resourcemanager.get_project_name()
        all_instances = self.all_instances
        for instance in all_instances:
            if instance.deletion_protection == False:
                result_num += 1
        if result_num > 0:
            result.append({project_name:result_num})
            return result
        else:
            pass


    # def list_router(self):
    #     client = compute_v1.RoutersClient()
    #     request = compute_v1.ListRoutersRequest(
    #         project=self.project
    #         )
    #     page_result = client.list(request=request)
    #     for response in page_result:
    #         print(response)        

# aa = Compute('speedy-victory-336109')
# print(aa.list_no_deletion_protection())