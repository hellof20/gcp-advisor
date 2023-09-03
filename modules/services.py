from google.cloud import servicemanagement_v1

def list_enabled_services(project):
    result = []
    client = servicemanagement_v1.ServiceManagerClient()
    request = servicemanagement_v1.ListServicesRequest(
        consumer_id = "project:"+project
    )
    page_result = client.list_services(request=request)
    for response in page_result:
        result.append(response.service_name) 
    return result