import click
import os
from multiprocessing import Pool
from common import write_csv,write_csv_header
from compute import Compute
from monitoring import Monitor
from resourcemanager import ResourceManager
from redis import Redis


@click.command()
@click.option("--projects", prompt="project_ids", help="项目id，多个项目用逗号分隔")


def main(projects):
    project_list = projects.split(',')
    for project in project_list:
        resouce = ResourceManager(project)
        project_name = resouce.get_project_name()
        csv_name = 'check_result.csv'
        if os.path.exists(csv_name):
            os.remove(csv_name)
        write_csv_header(csv_name)
        compute = Compute(project)
        monitor = Monitor(project)
        redis = Redis(project)
        try:
            write_csv(csv_name, project_name, compute.list_idle_ips(), pillar_name = '成本', product_name = 'VPC', check_name = '检查是否有未挂载的空闲外网IP')
            write_csv(csv_name, project_name, compute.list_idle_disks(), pillar_name = '成本', product_name = '磁盘', check_name = '检查是否有未挂载的磁盘')
            write_csv(csv_name, project_name, monitor.quota_usage(), pillar_name = '安全', product_name = '配额', check_name = '检查当前配额是否有高于70%的情况')
            write_csv(csv_name, project_name, redis.check_redis_maintain_window(), pillar_name = '安全', product_name = 'Redis', check_name = '检查Redis实例是否设置了维护窗口')
            write_csv(csv_name, project_name, redis.check_redis_ha(), pillar_name = '可靠性', product_name = 'Redis', check_name = '检查Redis实例是否启用高可用')
            write_csv(csv_name, project_name, redis.check_redis_rdb(), pillar_name = '可靠性', product_name = 'Redis', check_name = '检查Redis实例是否启用RDB备份')
        except  Exception as e:
            pass
        continue
        print('%s completed' % project_name)

if __name__ == '__main__':
    main()