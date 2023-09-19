import click
import os,sys
from multiprocessing import Pool
from common import write_csv,write_csv_header
from modules.services import list_enabled_services
from modules.compute import Compute
from modules.monitoring import Monitor
from modules.resourcemanager import ResourceManager
from modules.redis import Redis
from modules.gke import GKE
from modules.sql import SQL
from modules.gcs import GCS
from modules.contacts import Contacts
from modules.cloudlogging import Logging
from modules.artifact import Registry
from loguru import logger
from google.cloud import bigquery
import datetime

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("-p", "--projects", prompt="project_ids", help="Required: one or more project id separated by commas")
@click.option("-x", "--parallel", is_flag=True, help="Optional: check multiple projects in parallel")
@click.option("--debug", is_flag=True, help="Optional: set log level to debug")
# @click.option("--pillars", default = "all", required=False, help="Optional: one or more pillars you want to check, separated by commas. Choose from security,cost,availability,operation. Default is all.")


def main(projects, **kwargs):
    parallel = kwargs['parallel']
    debug = kwargs['debug']
    if debug:
        logger.remove()
        logger.add(sys.stdout, level='DEBUG')
    else:
        logger.remove()
        logger.add(sys.stdout, level='INFO', format="<level>{time} | {level} | {message}</level>")
    csv_name = 'check_result.csv'
    if os.path.exists(csv_name):
        os.remove(csv_name)
    write_csv_header(csv_name)
    project_list = projects.split(',')
    if parallel:
        logger.success('Begin to check all projects in parallel ...')
        p = Pool(len(project_list))
        for project in project_list:
            p.apply_async(func, args=(csv_name, project,))
        p.close()
        p.join()
        logger.success('All check success.')
    else:
        logger.success('Begin to check all projects in sequence ...')
        for project in project_list:
            func(csv_name, project)
        logger.success('All checks done.')
    logger.info('Begin to generate report ...')
    try:
        save_result_to_bq_looker(csv_name)
    except Exception as e:
        logger.warning('Generate report failed.')


def func(csv_name, project):
    logger.info('Checking project %s enabled services ...' % project)
    try:
        enabled_services = list_enabled_services(project)
    except Exception as e:
        logger.error(e)

    try:
        logger.debug('%s: Get project name' % project) 
        resource = ResourceManager(project)
        project_name = resource.get_project_name()
    except Exception as e:
        project_name = project
        logger.warning(e)

    if 'compute.googleapis.com' in enabled_services:
        logger.info('Checking project %s Compute Engine service ...' % project_name)
        compute = Compute(project)
        write_csv(csv_name, project_name, compute.list_no_deletion_protection(), pillar_name = '安全', product_name = 'VM', check_name = '实例未启用删除保护')
        write_csv(csv_name, project_name, compute.list_ephemeral_ip_vm(), pillar_name = '安全', product_name = 'VM', check_name = '实例公网IP为临时IP')
        write_csv(csv_name, project_name, compute.list_idle_ips(), pillar_name = '成本', product_name = 'VPC', check_name = '空闲公网IP')
        write_csv(csv_name, project_name, compute.list_idle_disks(), pillar_name = '成本', product_name = 'Disk', check_name = '空闲磁盘')
        write_csv(csv_name, project_name, compute.list_no_snapshots_project(), pillar_name = '安全', product_name = 'Snapshot', check_name = '检查实例是否有快照')
        write_csv(csv_name, project_name, compute.list_expiring_soon_ssl_certificates(), pillar_name = '安全', product_name = 'Certificates', check_name = '30天内将过期的证书')
        write_csv(csv_name, project_name, compute.list_expired_ssl_certificates(), pillar_name = '安全', product_name = 'Certificates', check_name = '已过期证书')
        write_csv(csv_name, project_name, compute.list_ephemeral_external_ip_lb(), pillar_name = '安全', product_name = 'LB', check_name = 'LB的公网IP为临时IP')
        write_csv(csv_name, project_name, compute.list_disabled_log_svc(), pillar_name = '卓越运维', product_name = 'LB', check_name = 'LB后端服务未启用日志')
        write_csv(csv_name, project_name, compute.recommender_idle_vm(), pillar_name = '成本', product_name = 'VM', check_name = '空闲实例')
    else:
        logger.info('%s: Compute Engine not enabled.'% project_name)

    if 'sqladmin.googleapis.com' in enabled_services:
        logger.info('Checking project %s Cloud SQL service ...' % project_name)
        sql = SQL(project)
        write_csv(csv_name, project_name, sql.check_sql_maintenance(), pillar_name = '可靠性', product_name = 'SQL', check_name = 'SQL实例未配置维护窗口')
        write_csv(csv_name, project_name, sql.check_sql_ha(), pillar_name = '可靠性', product_name = 'SQL', check_name = 'SQL实例未开启高可用')        
        write_csv(csv_name, project_name, sql.check_sql_delete_protect(), pillar_name = '安全', product_name = 'SQL', check_name = 'SQL实例未启用删除保护')        
        write_csv(csv_name, project_name, sql.check_sql_public_access(), pillar_name = '安全', product_name = 'SQL', check_name = 'SQL实例开放公网')        
        write_csv(csv_name, project_name, sql.check_sql_query_insight(), pillar_name = '卓越运维', product_name = 'SQL', check_name = 'SQL实例未启用QueryInsight')
        write_csv(csv_name, project_name, sql.check_sql_storage_auto_resize(), pillar_name = '可靠性', product_name = 'SQL', check_name = 'SQL实例未启用磁盘自动增长')
        write_csv(csv_name, project_name, sql.check_sql_slow_query(), pillar_name = '卓越运维', product_name = 'SQL', check_name = 'SQL实例慢日志未启用')
        write_csv(csv_name, project_name, sql.recommender_idle_sql(), pillar_name = '成本', product_name = 'SQL', check_name = '空闲SQL实例')   
    else:
        logger.info('%s: Cloud SQL not enabled.'% project_name)

    if 'redis.googleapis.com' in enabled_services:
        logger.info('Checking project %s Cloud Memorystore service ...' % project_name)
        redis = Redis(project)
        write_csv(csv_name, project_name, redis.check_redis_ha(), pillar_name = '可靠性', product_name = 'Redis', check_name = 'Redis实例未启用高可用')
        write_csv(csv_name, project_name, redis.check_redis_rdb(), pillar_name = '可靠性', product_name = 'Redis', check_name = 'Redis实例未启用RDB备份') 
        write_csv(csv_name, project_name, redis.check_redis_maintain_window(), pillar_name = '安全', product_name = 'Redis', check_name = 'Redis实例未设置维护窗口')  
    else:
        logger.info('%s: Redis not enabled.'% project_name)

    if 'container.googleapis.com' in enabled_services:
        logger.info('Checking project %s GKE service ...' % project_name)
        gke = GKE(project)
        write_csv(csv_name, project_name, gke.check_gke_nodepool_upgrade(), pillar_name = '可靠性', product_name = 'GKE', check_name = 'GKE节点组自动升级未关闭')
        write_csv(csv_name, project_name, gke.check_gke_static_version(), pillar_name = '可靠性', product_name = 'GKE', check_name = 'GKE控制面版本不是静态版本')
        write_csv(csv_name, project_name, gke.check_gke_controller_regional(), pillar_name = '可靠性', product_name = 'GKE', check_name = 'GKE控制面不是区域级')
        write_csv(csv_name, project_name, gke.check_gke_public_cluster(), pillar_name = '安全', product_name = 'GKE', check_name = 'GKE集群为公开集群')       
    else:
        logger.info('%s: GKE not enabled.'% project_name)

    if 'monitoring.googleapis.com' in enabled_services:
        logger.info('Checking project %s Monitoring service ...' % project_name)        
        monitor = Monitor(project)
        write_csv(csv_name, project_name, monitor.quota_usage(), pillar_name = '卓越运维', product_name = 'Quota', check_name = '配额高于70%')
    else:
        logger.info('%s: Cloud Monitoring not enabled.'% project_name)   

    if 'logging.googleapis.com' in enabled_services:
        logger.info('Checking project %s Logging service ...' % project_name)        
        log = Logging(project)
        write_csv(csv_name, project_name, log.check_if_analytics_enabled(), pillar_name = '卓越运维', product_name = 'Logging', check_name = '未启用日志分析功能')    
    else:
        logger.info('%s: Cloud Logging not enabled.'% project_name) 
    
    logger.info('Checking project %s Essential Contacts service ...' % project_name)        
    contacts = Contacts(project)
    write_csv(csv_name, project_name, contacts.list_essential_contacts(), pillar_name = '卓越运维', product_name = 'IAM', check_name = '未配置重要联系人') 

    if 'storage.googleapis.com' in enabled_services:
        logger.info('Checking project %s Storage service ...' % project_name)         
        gcs = GCS(project)
        write_csv(csv_name, project_name, gcs.list_public_buckets(), pillar_name = '安全', product_name = 'GCS', check_name = '存储桶允许公开访问')
    else:
        logger.info('%s: Cloud Storage not enabled.'% project_name)


    if 'artifactregistry.googleapis.com' in enabled_services:
        logger.info('Checking project %s ArtifactRegistry service ...' % project_name)  
        registry = Registry(project)
        write_csv(csv_name, project_name, registry.check_artifact_registry_redirection(), pillar_name = '安全', product_name = 'ArtifactRegistry', check_name = 'ContainerRegistry迁移到ArtifactRegistry')
        write_csv(csv_name, project_name, registry.list_no_tag_docker_images(), pillar_name = '成本', product_name = 'ArtifactRegistry', check_name = '没有tag的Docker image')
    else:
        logger.info('%s: ArtifactRegistry not enabled.'% project_name)


def save_result_to_bq_looker(csv_name):
    # Get bigquery client
    client = bigquery.Client()
    
    # Create a new database
    dataset_name = "gcp_adviser"
    dataset_id = f"{client.project}.{dataset_name}"
    dataset = bigquery.Dataset(dataset_id)
    try:
        dataset = client.create_dataset(dataset)
        logger.debug("Dataset {} crated.".format(dataset_id))
    except:
        logger.debug("Dataset {} already exists.".format(dataset_id))
    
    # Create a table.
    current_time = datetime.datetime.now().strftime('%m-%d-%H-%M')
    table_name = csv_name.split(".")[0] + "_" + current_time
    table_id = dataset_id + "." + table_name
    schema = [
        bigquery.SchemaField("project_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("pillar_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("product_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("check_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("result", "STRING", mode="NULLABLE"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table)
    
    # Write data from file to table.
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=False,
    )
    with open(csv_name, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_id, job_config=job_config)
    job.result()  # Waits for the job to complete.
    table = client.get_table(table_id)
    logger.debug(
        "Loaded {} rows and {} columns to {}".format(
            table.num_rows, len(table.schema), table_id
        )
    )
    
    # Generate the looker studio report link
    dashbord_url= f"https://lookerstudio.google.com/reporting/create?c.reportId=6448880a-1db5-4a69-9145-72b4df88cd88&ds.ds0.connector=bigQuery&ds.ds0.type=TABLE&ds.ds0.projectId={client.project}&ds.ds0.datasetId={dataset_name}&ds.ds0.tableId={table_name}"
    logger.success("Report URL: " + dashbord_url)

    
if __name__ == '__main__':
    main()
