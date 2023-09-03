from google.cloud import monitoring_v3
from loguru import logger

class Monitor(object):
    def __init__(self, project):
        self.project = project
        self.monitor = monitoring_v3.QueryServiceClient()

    def quota_usage(self):
        logger.debug('%s: quota_usage' % self.project)          
        result = []        
        try:
            threshold = 0.7
            query= '''
            fetch consumer_quota
            | { metric 'serviceruntime.googleapis.com/quota/allocation/usage'; metric 'serviceruntime.googleapis.com/quota/limit' }
            | every 1d
            | outer_join 0
            | div
            | group_by [metric.quota_metric,resource.location,resource.project_id]
            '''
            request = monitoring_v3.QueryTimeSeriesRequest(
                name="projects/%s" % self.project,
                query=query,
            )
            page_result = self.monitor.query_time_series(request=request)
            for response in page_result:
                quota_metric = response.label_values[0].string_value
                location = response.label_values[1].string_value
                project_id = response.label_values[2].string_value
                point_data = response.point_data[0].values[0].double_value
                if point_data > threshold:
                    # print("%s %s quota usage is %.2f"  %(project_id, quota_metric, point_data))
                    result.append("%s quota is %.2f"%(quota_metric, point_data*100))
        except Exception as e:
            logger.warning(e)
        finally:
            return result

# aa = Monitor('speedy-victory-336109')
# print(aa.quota_usage())