from google.cloud import compute_v1

class Compute(object):
    def __init__(self, project):
        self.project = project

    def list_all_instances(self):
        result = []
        instance_client = compute_v1.InstancesClient()
        request = {"project" : self.project}
        agg_list = instance_client.aggregated_list(request=request)
        for zone, response in agg_list:
            if response.instances:
                for instance in response.instances:
                    result.append(instance.name)
        return result

    def list_idle_ips(self):
        result = []
        address_client = compute_v1.AddressesClient()
        request = compute_v1.AggregatedListAddressesRequest(project=self.project)
        page_result = address_client.aggregated_list(request=request)
        for region,response in page_result:
            if response.addresses:
                for address in response.addresses:
                    if address.status == 'RESERVED':
                        result.append(address.address)
        return result

    def list_idle_disks(self):
        result = []
        address_client = compute_v1.AddressesClient()
        request = compute_v1.AggregatedListAddressesRequest(project=self.project)
        page_result = address_client.aggregated_list(request=request)
        for region,response in page_result:
            if response.addresses:
                for address in response.addresses:
                    if address.status == 'RESERVED':
                        result.append(address.address)
        return result

    def list_idle_disks(self):
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

# aa = Compute('speedy-victory-336109')   
# aa. list_idle_disks()                