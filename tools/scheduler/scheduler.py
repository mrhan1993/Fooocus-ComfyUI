from apis.models.remote_host import FilterHost, RemoteHostsDB, RemoteHostDB


def filter_hosts(hosts: RemoteHostsDB, conditions: FilterHost) -> list[RemoteHostDB]:
    """
    根据给定的条件筛选主机列表，返回符合条件的主机列表。
    挑选逻辑：
        - 指定 host_name 或者 host_ip 将直接选择对应主机，忽略其他条件
        - 主机属性或者筛选条件的值为 0 或者空值表示无条件匹配
        - 给定的筛选规则为逻辑与
    :param conditions: 筛选条件
    :param hosts: 主机列表
    :return: 返回一个初步筛选的主机列表
    """
    # 检查是否提供了 host_name 或 host_ip
    conditions = conditions.model_dump()
    if 'host_name' in conditions:
        for host in hosts.hosts:
            if host.host_name == conditions['host_name']:
                return [host]
    elif 'host_ip' in conditions:
        for host in hosts.hosts:
            if host.host_ip == conditions['host_ip']:
                return [host]

    # 如果没有提供 host_name 或 host_ip，则根据其他条件筛选
    filtered_hosts = []
    for host in hosts.hosts:
        if not host.alive:
            continue
        match = True
        for key, value in conditions.items():
            if key in ['video_ram', 'memory', 'cpu_cores', 'flops']:
                if value != 0 and getattr(host, key) != 0 and getattr(host, key) < value:
                    match = False
                    break
            elif key == 'gpu_model':
                if value != "" and host.gpu_model != "":
                    if host.key != value:
                        match = False
                        break
            elif key == 'labels':
                # if value != {} and host.labels != {}:
                if value != {}:
                    if not all(item in host.labels.items() for item in value.items()):
                        match = False
                        break
        if match:
            filtered_hosts.append(host)

    return filtered_hosts
