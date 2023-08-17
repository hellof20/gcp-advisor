from google.cloud import compute_v1

class Compute(object):
    def __init__(self, project):
        self.project = project

    def list_all_instances(self):
        try:
            result = []
            instance_client = compute_v1.InstancesClient()
            request = {"project" : self.project}
            agg_list = instance_client.aggregated_list(request=request)
            for zone, response in agg_list:
                if response.instances:
                    for instance in response.instances:
                        print(instance)
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
                    for instance in response.instances:
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


    def list_vm_zone(self):
        try:
            result = []
            print(self.list_all_instances_zones())
        except:
            pass    

# aa = Compute('pangu-358004')
# print(aa.list_all_instances())