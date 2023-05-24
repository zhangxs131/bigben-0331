"""
工程配置文件，剥离了部分可配置的参数，在这里统一修改，配置。
暂时未区分不同环境的配置文件，如果有需要，可以新建子类
DevConfig，ProdConfig来区分
"""
import os.path


class ProjectConfig:
    # cos相关配置
    cos_secret_id = ''  # 桶id
    cos_secret_key = ''  # 桶key
    cos_region = ''  # 服务区域
    cos_bucket = ''  # 桶名称
    cos_start_prefix = ''  # 前缀
    use_cos_for_models = False  # 是否使用cos

    # 模型版本
    model_version = 'v1'  # 模型版本，默认从v1开始迭代
    model_path = os.path.abspath(os.path.join(os.path.abspath(__file__), '../dep')) # 配置模型保存路径
    model_name = 'model.json'

    # 其他配置
    reload_version_key = 'version'  # 重新加载模型时入参key
    company_name = 'company' #快递公司code "zto yuantong yunda"
    user_address_name = 'user_address'  # 用户地址 三级
    current_address_name = 'current_address'  # 当前轨迹的二级地址
    request_param_input = [company_name,user_address_name, current_address_name]  # 请求POST body中入参key

    company_code_dict={'zto':"中通",'yunda':'韵达','yuantong':'圆通'}
    #company_name_dict={v:k for k,v in company_code_dict.items()}

# {
#     'company':'zto',
#     'user_address':'北京-北京市-海淀区',
#     'current_address':'天津市'
# }