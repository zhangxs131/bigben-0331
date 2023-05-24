"""
一些通用函数存放文件，当前包含LazyInit类，set_log函数。
LazyInit 在模型文件巨大，启动非常耗时情况下启用。
具体用法是在model外再封装一层LazyInit，从get_instance
方法获取模型实例。

set_log函数是配置日志所用
"""

import logging


class LazyInit:
    def __init__(self, instance_init_fun):
        self.instance_init_fun = instance_init_fun
        self.instance = None

    def get_instance(self):
        if not self.instance:
            self.instance = self.instance_init_fun()
        return self.instance


def set_log(log_file_name='app-logs.log'):
    # 输出到屏幕
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(
        logging.Formatter(
            '%(asctime)s '
            '%(filename)s '
            '%(funcName)s'
            '[line:%(lineno)d] '
            '[%(levelname)s] '
            '%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    )

    # 输出到日志
    # fh = logging.FileHandler(log_file_name, mode='a')
    # fh.setLevel(logging.INFO)
    # fh.setFormatter(
    #     logging.Formatter(
    #         '%(asctime)s '
    #         '%(filename)s '
    #         '%(funcName)s'
    #         '[line:%(lineno)d] '
    #         '[%(levelname)s] '
    #         '%(message)s',
    #         datefmt='%Y-%m-%d %H:%M:%S'
    #     )
    # )

    logging.basicConfig(level=logging.INFO, handlers=[sh])
