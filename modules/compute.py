from google.cloud import compute_v1
from google.cloud import recommender_v1
from datetime import datetime,timedelta, timezone
from loguru import logger


class Compute(object):
    def __init__(self, project):
        self.project = project
        self.all_instances = self.list_all_instances()
        self.ips = self.list_ips()
        self.ssl_certificates = self.list_ssl_certificates()
        self.recommender_client = recommender_v1.RecommenderClient()
        self.instance_zones = self.list_all_instances_zones()


    def list_all_instances(self):
        logger.debug('%s: list_all_instances' % self.project)   
        result = []
        try:
            instance_client = compute_v1.InstancesClient()
            request = {"project" : self.project}
            agg_list = instance_client.aggregated_list(request=request)
            for zone, response in agg_list:
                if response.instances:
                    for instance in response.instances:
                        result.append(instance)
        except Exception as e:
            logger.warning(e)
        finally:
            return result            


    def list_ips(self):
        logger.debug('%s: list_ips' % self.project)   
        result = []
        try:
            address_client = compute_v1.AddressesClient()
            request = compute_v1.AggregatedListAddressesRequest(project=self.project)
            page_result = address_client.aggregated_list(request=request)
            for region,response in page_result:
                if response.addresses:
                    for address in response.addresses: 
                        result.append(address)
        except Exception as e:
            logger.warning(e)
        finally:
            return result            


    def list_ssl_certificates(self):
        logger.debug('%s: list_ssl_certificates' % self.project)   
        result = []        
        try:
            expired_num = 0
            expiring_soon_num = 0
            client = compute_v1.SslCertificatesClient()
            request = compute_v1.ListSslCertificatesRequest(project=self.project,)
            page_result = client.list(request=request)
            for response in page_result:
                result.append(response)
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def list_all_instances_zones(self):
        logger.debug('%s: list_all_instances_zones' % self.project)   
        result = []        
        try:
            instance_client = compute_v1.InstancesClient()
            request = {"project" : self.project}
            agg_list = instance_client.aggregated_list(request=request)
            for zone, response in agg_list:
                if response.instances:
                        result.append(zone.split('/')[-1])
            return result
        except Exception as e:
            logger.warning(e)
        finally:
            return result    


    def list_idle_ips(self):
        logger.debug('%s: list_idle_ips' % self.project)           
        result = []        
        try:
            for address in self.ips:
                if address.status == 'RESERVED' and address.address_type == 'EXTERNAL':
                    result.append(address.address)
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def list_idle_disks(self):
        logger.debug('%s: list_idle_disks' % self.project)             
        result = []        
        try:
            disk_client = compute_v1.DisksClient()
            request = compute_v1.AggregatedListDisksRequest(project=self.project)
            page_result = disk_client.aggregated_list(request=request)
            for zone,response in page_result:
                if response.disks:
                    for disk in response.disks:
                        if not disk.users:
                            result.append("%s: %sGB" % (disk.name, disk.size_gb))
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def list_all_regions(self):
        logger.debug('%s: list_all_regions' % self.project)            
        result = []
        try:
            client = compute_v1.RegionsClient()
            request = compute_v1.ListRegionsRequest(project=self.project)
            page_result = client.list(request=request)
            for response in page_result:
                result.append(response.name)
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def list_no_snapshots_project(self):
        logger.debug('%s: list_no_snapshots_project' % self.project)   
        result = []        
        try:
            client = compute_v1.SnapshotsClient()
            request = compute_v1.ListSnapshotsRequest(project=self.project)
            page_result = client.list(request=request)
            for response in page_result:
                result.append(response.name)
            if len(result) == 0:
                result = ['No Snapshots']
            else:
                result = []
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def list_no_deletion_protection(self):
        logger.debug('%s: list_no_deletion_protection' % self.project)   
        result = []        
        try:
            all_instances = self.all_instances
            for instance in all_instances:
                if instance.deletion_protection == False and instance.name[0:4] != 'gke-':
                    result.append(instance.name)
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def list_ephemeral_ip_vm(self):
        logger.debug('%s: list_ephemeral_ip_vm' % self.project)           
        result = []        
        try:
            # VPC IP list
            address_list = []
            for address in self.ips:
                address_list.append(address.address)
            # VM external IP list
            vm_address_list = []            
            for instance in self.all_instances:
                if instance.name[0:4] != 'gke-':  # 去掉GKE节点
                    for network in instance.network_interfaces:
                        for i in network.access_configs:
                            vm_address_list.append(i.nat_i_p)
            # check if VM external IP in VPC IP list
            for i in vm_address_list:
                if (i not in address_list) and i != '':
                    result.append(i)
        except Exception as e:
            logger.warning(e)
        finally:
            return result


    def list_expired_ssl_certificates(self):
        logger.debug('%s: list_expired_ssl_certificates' % self.project)   
        result = []
        try:
            current_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
            for response in self.ssl_certificates:
                if 'expire_time' in response:
                    expire_time_utc = datetime.strptime(response.expire_time,"%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=timezone.utc)
                    remaining_days = (expire_time_utc - current_utc).days
                    if remaining_days < 0:
                        result.append(response.name)
        except Exception as e:
            logger.warning(e)
        finally:
            return result              


    def list_expiring_soon_ssl_certificates(self):
        logger.debug('%s: list_expiring_soon_ssl_certificates' % self.project)       
        result = []            
        try:        
            current_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
            for response in self.ssl_certificates:
                if 'expire_time' in response:
                    expire_time_utc = datetime.strptime(response.expire_time, "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=timezone.utc)
                    remaining_days = (expire_time_utc - current_utc).days
                    if remaining_days >= 0 and remaining_days < 30:
                        result.append("%s: %s days "%(response.name, remaining_days))
        except Exception as e:
            logger.warning(e)
        finally:
            return result 


    def list_ephemeral_external_ip_lb(self):
        logger.debug('%s: list_ephemeral_external_ip_lb' % self.project)   
        result = []        
        try:
            # VPC IP list
            address_list = []
            for address in self.ips:
                address_list.append(address.address)
            # LB IP list
            lb_ip_list = []
            client = compute_v1.ForwardingRulesClient()
            request = compute_v1.AggregatedListForwardingRulesRequest(
                project = self.project,
            )
            page_result = client.aggregated_list(request=request)        
            for region, response in page_result:
                if response.forwarding_rules:
                    for forwarding_rule in response.forwarding_rules:
                        if forwarding_rule.load_balancing_scheme not in ('INTERNAL', 'INTERNAL_MANAGED'):
                            lb_ip_list.append(forwarding_rule.I_p_address)
            # check if LB external IP in VPC IP list
            for i in lb_ip_list:
                if (i not in address_list):
                    result.append(i)
        except Exception as e:
            logger.warning(e)
        finally:
            return result          


    def list_disabled_log_svc(self):
        logger.debug('%s: list_disabled_log_svc' % self.project)   
        result = []        
        try:
            client = compute_v1.BackendServicesClient()
            request = compute_v1.ListBackendServicesRequest(
                project = self.project,
            )
            page_result = client.list(request=request)
            for response in page_result:
                if response.log_config.enable == False:
                    result.append(response.name)
        except Exception as e:
            logger.warning(e)
        finally:
            return result 


    def recommender_idle_vm(self):
        logger.debug('%s: recommender_idle_vm' % self.project)          
        result = []
        try:
            for zone in self.instance_zones:
                parent = 'projects/%s/locations/%s/recommenders/%s' %(self.project, zone, 'google.compute.instance.IdleResourceRecommender')
                request = recommender_v1.ListRecommendationsRequest(parent=parent)
                page_result = self.recommender_client.list_recommendations(request=request)
                for response in page_result:
                    vm_name = response.content.overview['resource'].split('/')[-1]
                    result.append(vm_name)
        except Exception as e:
            logger.warning(e)
        finally:
            return result