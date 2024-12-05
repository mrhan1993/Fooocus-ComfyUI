import math


def calculate_weight(memory_gb: int, tflops: float, num_tasks: int,
                     base_tflops: float = 1.0, alpha=1.0, beta=1.0, gamma=1.5) -> float:
    """
    计算主机权重
    :param memory_gb: 显存大小（GB）
    :param tflops: 主机计算性能（TFlops）
    :param num_tasks: 当前运行的任务数量
    :param base_tflops: 集群中基准 TFlops（最低性能）
    :param alpha: 显存权重系数
    :param beta: TFlops 权重系数
    :param gamma: 任务数量权重系数
    :return: 主机权重
    """

    # 显存权重计算
    if memory_gb < 8:
        memory_weight = 1
    else:
        memory_weight = 1 + math.log2(memory_gb / 8)

    # TFlops 权重计算
    tflops_weight = tflops / base_tflops

    # 任务数量权重计算
    # task_weight = 1 / (1 + num_tasks)

    # 总权重计算
    total_weight = alpha * memory_weight + beta * tflops_weight - gamma * num_tasks
    return total_weight
