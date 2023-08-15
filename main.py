import click
import os
from multiprocessing import Pool
from common import write_csv,write_csv_header
from compute import Compute
from monitoring import Monitor
from resourcemanager import ResourceManager


@click.command()
@click.option("--projects", prompt="project_ids", help="项目id，多个项目用逗号分隔")


def main(projects):
    project_list = projects.split(',')
    os.remove('check_result.csv')
    write_csv_header()
    with Pool(len(project_list)) as p:
        p.map(check_function, project_list)

def check_function(project):
    resouce = ResourceManager(project)
    project_name = resouce.get_project_name()
    compute = Compute(project)
    monitor = Monitor(project)
    write_csv(project_name = project_name, result = compute.list_idle_ips(), pillar_name = '成本', product_name = 'VPC', check_name = '检查是否有未挂载的空闲外网IP')
    write_csv(project_name = project_name, result = compute.list_idle_disks(), pillar_name = '成本', product_name = '磁盘', check_name = '检查是否有未挂载的磁盘')
    write_csv(project_name = project_name, result = monitor.quota_usage(), pillar_name = '安全', product_name = '配额', check_name = '检查当前配额是否有高于70%的情况')

if __name__ == '__main__':
    main()