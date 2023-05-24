import os
from abc import ABC, abstractmethod

from coscmd.cos_threadpool import SimpleThreadPool
from qcloud_cos import CosConfig, CosS3Client, CosServiceError

from config import ProjectConfig


class Downloader(ABC):
    """
    下载模型抽象基类
    """
    @abstractmethod
    def download(self):
        raise NotImplementedError


class CosDownloader(Downloader):
    def __init__(self, local_dir='./'):
        self.local_dir = local_dir  # 工程中模型文件本地存放位置
        self.secret_id = ProjectConfig.cos_secret_id  # 桶id
        self.secret_key = ProjectConfig.cos_secret_key  # 桶key
        self.region = ProjectConfig.cos_region  # 服务区域
        self.bucket = ProjectConfig.cos_bucket  # 桶名称
        self.start_prefix = ProjectConfig.cos_start_prefix  # 前缀
        self.token = None
        self.scheme = 'https'
        self.config = CosConfig(Region=self.region, SecretId=self.secret_id,
                                SecretKey=self.secret_key, Token=self.token, Scheme=self.scheme)
        self.client = CosS3Client(self.config)
        self.delimiter = ''
        self.bucket_file_infos = []

    def _list_current_dir(self, prefix):
        file_infos = []
        sub_dirs = []
        marker = ""
        count = 1
        while True:
            response = self.client.list_objects(
                self.bucket, prefix, self.delimiter, marker)
            count += 1
            if "CommonPrefixes" in response:
                common_prefixes = response.get("CommonPrefixes")
                sub_dirs.extend(common_prefixes)
            if "Contents" in response:
                contents = response.get("Contents")
                file_infos.extend(contents)
            if "NextMarker" in response.keys():
                marker = response["NextMarker"]
            else:
                break
        # 如果 delimiter 设置为 "/"，则需要进行递归处理子目录，
        # sorted(sub_dirs, key=lambda sub_dir: sub_dir["Prefix"])
        # for sub_dir in sub_dirs:
        #     print(sub_dir)
        #     sub_dir_files = listCurrentDir(sub_dir["Prefix"])
        #     file_infos.extend(sub_dir_files)
        sorted(file_infos, key=lambda file_info: file_info["Key"])
        for file in file_infos:
            print(file)
        return file_infos

    # 下载文件到本地目录，如果本地目录已经有同名文件则会被覆盖；
    # 如果目录结构不存在，则会创建和对象存储一样的目录结构
    def _download_files(self, file_infos):
        pool = SimpleThreadPool()
        for file in file_infos:
            # 文件下载 获取文件到本地
            file_cos_key = file["Key"]
            local_name = self.local_dir + file_cos_key[len(self.start_prefix):]
            # 如果本地目录结构不存在，递归创建
            if not os.path.exists(os.path.dirname(local_name)):
                os.makedirs(os.path.dirname(local_name))
            # skip dir, no need to download it
            if str(local_name).endswith("/"):
                continue
            # 使用线程池方式
            pool.add_task(self.client.download_file,
                          self.bucket, file_cos_key, local_name)
            # 简单下载方式
            # response = client.get_object(
            #     Bucket=test_bucket,
            #     Key=file_cos_key,
            # )
            # response['Body'].get_stream_to_file(localName)
        pool.wait_completion()

    def download(self):
        try:
            self.bucket_file_infos = self._list_current_dir(self.start_prefix)
        except CosServiceError as e:
            print(e.get_origin_msg())
            print(e.get_digest_msg())
            print(e.get_status_code())
            print(e.get_error_code())
            print(e.get_error_msg())
            print(e.get_resource_location())
            print(e.get_trace_id())
            print(e.get_request_id())
        self._download_files(self.bucket_file_infos)
