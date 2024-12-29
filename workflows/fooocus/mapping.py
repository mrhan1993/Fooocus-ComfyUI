import random


def mapped_workflow(workflow: dict, requests: dict, mapping: dict) -> dict:
    """
    Maps the requests to the workflow
    :param workflow: 待赋值的 workflow 字典
    :param requests: 请求参数
    :param mapping: 两个字典的参数映射
    """
    def set_nested_value(d, keys, value):
        """Recursively set a nested dictionary value."""
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    def get_nested_value(d, keys):
        """Recursively get a nested dictionary value."""
        for key in keys:
            if isinstance(d, dict) and key in d:
                d = d[key]
            else:
                return None
        return d

    for key_workflow, key_request in mapping.items():
        v = get_nested_value(requests, key_request)
        if v is not None:
            if isinstance(v, bool) and v:
                v = "enabled"
            if isinstance(v, bool) and not v:
                v = "disable"
            set_nested_value(workflow, key_workflow, v)
    return workflow


def post_mapped_fooocus(workflow: dict) -> dict:
    """
    处理一些额外的转换信息
    :param workflow: 已经完成映射的 workflow
    :return: workflow
    """
    # 处理数据类型
    style_section = workflow["36"]["inputs"]["style_selections"]
    workflow["36"]["inputs"]["style_selections"] = ", ".join(style_section) if len(style_section) > 0 else ""

    if workflow["42"]["inputs"]["seed"] == -1:
        workflow["42"]["inputs"]["seed"] = random.randint(0, 2 ** 64 - 1)

    try:
        workflow["25"]["inputs"]["outpaint_left"] = "enable" if "Left" in workflow["25"]["inputs"]["outpaint_left"] else "disable"
        workflow["25"]["inputs"]["outpaint_left_distance"] = workflow["25"]["inputs"]["outpaint_left_distance"][0]

        workflow["25"]["inputs"]["outpaint_right"] = "enable" if "Right" in workflow["25"]["inputs"]["outpaint_right"] else "disable"
        workflow["25"]["inputs"]["outpaint_right_distance"] = workflow["25"]["inputs"]["outpaint_right_distance"][2]

        workflow["25"]["inputs"]["outpaint_top"] = "enable" if "Top" in workflow["25"]["inputs"]["outpaint_top"] else "disable"
        workflow["25"]["inputs"]["outpaint_top_distance"] = workflow["25"]["inputs"]["outpaint_top_distance"][1]

        workflow["25"]["inputs"]["outpaint_bottom"] = "enable" if "Bottom" in workflow["25"]["inputs"]["outpaint_bottom"] else "disable"
        workflow["25"]["inputs"]["outpaint_bottom_distance"] = workflow["25"]["inputs"]["outpaint_bottom_distance"][3]
    except KeyError:
        pass
    return workflow
