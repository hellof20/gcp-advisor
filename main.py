import click
import os
from multiprocessing import Pool
from common import write_csv,write_csv_header
from compute import Compute
from monitoring import Monitor
from resourcemanager import ResourceManager
from recommender import Recommender
from redis import Redis
from gke import GKE
from sql import SQL
from contacts import Contacts


@click.command()
@click.option("--projects", prompt="project_ids", help="项目id，多个项目用逗号分隔")
# @click.option("--pillars", prompt="pillars", default = "all", help="项目id，多个项目用逗号分隔") todo


def main(projects):
    csv_name = 'check_result.csv'
    if os.path.exists(csv_name):
        os.remove(csv_name)
    write_csv_header(csv_name)
    project_list = projects.split(',')
    for project in project_list:
        resouce = ResourceManager(project)
        project_name = resouce.get_project_name()
        compute = Compute(project)
        monitor = Monitor(project)
        redis = Redis(project)
        gke = GKE(project)
        sql = SQL(project)
        recommender = Recommender(project)
        contacts = Contacts(project)
        write_csv(csv_name, project_name, compute.list_idle_ips(), pillar_name = '成本', product_name = 'VPC', check_name = '检查是否有未挂载的空闲外网IP')
        write_csv(csv_name, project_name, compute.list_idle_disks(), pillar_name = '成本', product_name = '磁盘', check_name = '检查是否有未挂载的磁盘')
        write_csv(csv_name, project_name, compute.list_no_snapshots_project(), pillar_name = '安全', product_name = 'Snapshot', check_name = '检查是否有快照')
        write_csv(csv_name, project_name, compute.list_no_deletion_protection(), pillar_name = '安全', product_name = 'VM', check_name = '检查未启用删除保护的VM数量')
        write_csv(csv_name, project_name, monitor.quota_usage(), pillar_name = '安全', product_name = '配额', check_name = '检查当前配额是否有高于70%的情况')        
        write_csv(csv_name, project_name, redis.check_redis_maintain_window(), pillar_name = '安全', product_name = 'Redis', check_name = '检查Redis实例是否设置了维护窗口')      
        write_csv(csv_name, project_name, redis.check_redis_ha(), pillar_name = '可靠性', product_name = 'Redis', check_name = '检查Redis实例是否启用高可用')
        write_csv(csv_name, project_name, redis.check_redis_rdb(), pillar_name = '可靠性', product_name = 'Redis', check_name = '检查Redis实例是否启用RDB备份')
        write_csv(csv_name, project_name, gke.check_gke_nodepool_upgrade(), pillar_name = '可靠性', product_name = 'GKE', check_name = '检查GKE节点组自动升级是否关闭')
        write_csv(csv_name, project_name, gke.check_gke_static_version(), pillar_name = '可靠性', product_name = 'GKE', check_name = '检查GKE控制面版本是否为静态版本')
        write_csv(csv_name, project_name, gke.check_gke_controller_regional(), pillar_name = '可靠性', product_name = 'GKE', check_name = '检查GKE控制面是否为区域级')
        write_csv(csv_name, project_name, sql.check_sql_maintenance(), pillar_name = '可靠性', product_name = 'SQL', check_name = '检查SQL实例是否设置了维护窗口')
        write_csv(csv_name, project_name, sql.check_sql_ha(), pillar_name = '可靠性', product_name = 'SQL', check_name = '检查SQL实例是否开启高可用')        
        write_csv(csv_name, project_name, sql.check_sql_delete_protect(), pillar_name = '安全', product_name = 'SQL', check_name = '检查SQL实例是否启用删除保护')        
        write_csv(csv_name, project_name, sql.check_sql_public_access(), pillar_name = '安全', product_name = 'SQL', check_name = '检查SQL实例是否允许0.0.0.0访问')        
        write_csv(csv_name, project_name, sql.check_sql_query_insight(), pillar_name = '安全', product_name = 'SQL', check_name = '检查SQL实例是否启用了Query Insight')        
        write_csv(csv_name, project_name, sql.check_sql_storage_auto_resize(), pillar_name = '可靠性', product_name = 'SQL', check_name = '检查SQL实例是否启用磁盘自动增长')
        write_csv(csv_name, project_name, recommender.recommender_idle_vm(), pillar_name = '成本', product_name = 'VM', check_name = '检查空闲VM')        
        write_csv(csv_name, project_name, recommender.recommender_idle_sql(), pillar_name = '成本', product_name = 'SQL', check_name = '检查空闲SQL实例')
        write_csv(csv_name, project_name, contacts.list_essential_contacts(), pillar_name = '安全', product_name = 'IAM', check_name = '检查是否配置了重要联系人')
        
if __name__ == '__main__':
    main()