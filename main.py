from configs import store_conf
from tools.store.oss_client import OssClient
import oss2

qcloud = OssClient('qcloud', store_conf.qcloud_config)
aliyun = OssClient('aliyun', store_conf.ali_config)

# qcloud.upload_file("temp/2024-11-22_15-48-22_6311.jpeg", "input/test.jpeg")
# print(qcloud.get_file("input/test.jpeg"))
# qcloud.delete_file("input/test.jpeg")

# aliyun.upload_file("temp/2024-11-22_15-48-22_6311.jpeg", "input/test.jpeg")
# print(aliyun.get_file("input/test.jpeg"))
# aliyun.delete_file("input/test.jpeg")