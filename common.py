from csv import writer, DictWriter

def write_csv_header(csv_name):
    field_names = ['project_name','pillar_name', 'product_name','check_name','result']
    with open(csv_name, 'a') as f:
        writer_object = DictWriter(f, fieldnames=field_names)    
        writer_object.writeheader()
        f.close()

def write_csv(csv_name, project_name, result, pillar_name, product_name, check_name):
    field_names = ['project_name','pillar_name', 'product_name','check_name','result']
    dict_list = []
    dict = {}
    with open(csv_name, 'a', encoding='utf-8') as f:
        writer_object = DictWriter(f, fieldnames=field_names)
        if result:
            for i in result:
                dict['project_name'] = project_name
                dict['pillar_name'] = pillar_name
                dict['product_name'] = product_name
                dict['check_name'] = check_name
                dict['result'] = i
                writer_object.writerow(dict)
        f.close()