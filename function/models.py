import json
import os
from abc import ABC, abstractmethod

from config import ProjectConfig


class AbstractModel(ABC):

    @abstractmethod
    def predict(self, data, **kwargs):
        """在这里实现模型预测功能

        :param data: 预测所需要参数
        :param kwargs: 额外需要增加参数
        :return: 模型预测结果
        """
        raise NotImplementedError

    @abstractmethod
    def predict_score(self, data, **kwargs):
        """在这里实现模型预测（带有分数，置信度，概率等）

        :param data:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def format_predict(self, predict, **kwargs):
        """在这里实现预测结果后处理逻辑

        :param predict: 模型预测结果
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def format_predict_score(self, predict_score, **kwargs):
        """在这里实现带有分数、置信度、概率的模型预测结果后处理逻辑

        :param predict_score:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def pre_process(self, data_raw, **kwargs):
        """ 在这里实现数据预处理

        :param data_raw: 原始输入
        :param kwargs:
        :return: 数据预处理后的结果
        """
        raise NotImplementedError

    @abstractmethod
    def __init__(self, model_path, version, model_name, **kwargs):
        """在构造函数里实现模型加载等准备工作
        如：
            self.model = xxx.load(self.model_file_path)
        :param model_path: 模型路径
        :param version: 模型版本
        :param model_name: 模型名称
        :param kwargs:
        """
        raise NotImplementedError


class Model(AbstractModel):
    def predict(self, data, **kwargs):

        #数据错误获取缺失
        if type(data)!=dict:
            raise Exception('数据错误')

        predict = self.model[data[ProjectConfig.company_name]][data[ProjectConfig.user_address_name][0]][data[ProjectConfig.user_address_name][1]][data[ProjectConfig.user_address_name][2]][data[ProjectConfig.current_address_name]]
        return predict

    def predict_score(self, data, **kwargs):
        pass

    def format_predict(self, predict, **kwargs):
        return round(predict,3)

    def format_predict_score(self, predict_score, **kwargs):
        pass

    def pre_process(self, data_raw, **kwargs):
        company = data_raw[ProjectConfig.company_name]
        user_address = data_raw[ProjectConfig.user_address_name]
        current_address = data_raw[ProjectConfig.current_address_name]

        if company is None:
            raise Exception('Error :comany not exist')
        if user_address is None:
            raise Exception('Error :user_address not exist')
        if current_address is None:
            raise Exception('Error :current_address not exist')

        #将三级地址 - 进行分割，不足3段则返回error
        #二级地址 不需要 - 进行分割
        #company code 不需要处理，或者判断中文，转称code

        user_address=user_address.split('-')
        if len(user_address)!=3:
            raise Exception('Error :user_address format error')

        if company not in ProjectConfig.company_code_dict:
            raise Exception('Error :company code error,for now : zto ,yuantong,yunda')

        current_address=current_address.split('-')[-1]

        return {ProjectConfig.company_name:company,
                ProjectConfig.user_address_name: user_address,
                ProjectConfig.current_address_name: current_address}

    def __init__(self, model_path, version, model_name, **kwargs):
        """
        self.model_file_path = os.path.abspath(
            os.path.join(os.path.abspath(__file__),
                         f'../{model_path}/{version}/{model_name}'))
        """
        with open(f'{model_path}/{version}/{model_name}', 'r') as f:
            self.model = json.load(f)
        pass
