from google.cloud import compute_v1
from resourcemanager import ResourceManager
from datetime import datetime,timedelta, timezone

class Compute(object):
    def __init__(self, project):
        self.project = project
        self.all_instances = self.list_all_instances()
        self.ips = self.list_ips()
        self.ssl_certificates = self.list_ssl_certificates()

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


    def list_ips(self):
        try:
            result = []
            address_client = compute_v1.AddressesClient()
            request = compute_v1.AggregatedListAddressesRequest(project=self.project)
            page_result = address_client.aggregated_list(request=request)
            for region,response in page_result:
                if response.addresses:
                    for address in response.addresses: 
                        result.append(address)
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
            for address in self.ips:
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
                            result.append({disk.name:disk.size_gb})
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
        try:
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
        except:
            pass            


    def list_ephemeral_ip_vm(self):
        try:
            result = []
            address_list = []
            # VPC IP list
            vm_address_list = []
            for address in self.ips:
                address_list.append(address.address)
            # VM external IP list
            for instance in self.all_instances:
                for network in instance.network_interfaces:
                    for i in network.access_configs:
                        vm_address_list.append(i.nat_i_p)
            # check if VM external IP in VPC IP list
            for i in vm_address_list:
                if (i not in address_list):
                    result.append(i)
            return result
        except:
            pass

           
    def list_ssl_certificates(self):
        try:
            result = []
            expired_num = 0
            expiring_soon_num = 0
            client = compute_v1.SslCertificatesClient()
            request = compute_v1.ListSslCertificatesRequest(project=self.project,)
            page_result = client.list(request=request)
            for response in page_result:
                result.append(response)
            return result
        except:
            pass                


    def list_expired_ssl_certificates(self):
        try:
            result = []
            current_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
            for response in self.ssl_certificates:
                expire_time_utc = datetime.strptime(response.expire_time,"%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=timezone.utc)
                remaining_days = (expire_time_utc - current_utc).days
                if remaining_days < 0:
                    result.append(response.name)
            return result
        except:
            pass                


    def list_expiring_soon_ssl_certificates(self):
        try:        
            result = []
            current_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
            for response in self.ssl_certificates:
                expire_time_utc = datetime.strptime(response.expire_time,"%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=timezone.utc)
                remaining_days = (expire_time_utc - current_utc).days
                if remaining_days >= 0 and remaining_days < 30:
                    result.append({response.name: remaining_days})
            return result
        except:
            pass                


# if remaining_days >= 0 and remaining_days < 30:
#                 expiring_soon_num += 1

    # def list_router(self):
    #     client = compute_v1.RoutersClient()
    #     request = compute_v1.ListRoutersRequest(
    #         project=self.project
    #         )
    #     page_result = client.list(request=request)
    #     for response in page_result:
    #         print(response)        

# aa = Compute('speedy-victory-336109')
# print(aa.list_expiring_soon_ssl_certificates())