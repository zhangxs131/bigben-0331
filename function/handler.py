import json
import logging
from urllib import parse

from config import ProjectConfig
from download import CosDownloader
from models import Model

model = None  # 模型全局变量


def get_input_data_by_key_post1st(skey, dict_body, dict_query):
    """
    从query/body中获取指定key的提交信息，如果同时都存在则body数据优先，如果都没有则返回''
    NOTE: 通常不需要修改本函数
    """
    if skey in dict_body:
        return dict_body[skey]
    if skey in dict_query:
        return dict_body[skey]
    return None


def init():
    """init service， run once when starting
    NOTE: 通常不需要修改本函数
    """
    logging.info('initializing...')
    if ProjectConfig.use_cos_for_models:
        download_from_cloud()  # 模型需要从云端下载时使用
    reload_models(None)  # 初始化数据
    return True


def handle(event_obj):
    """handle a request to the function 
    Args:
        event_obj (obj): an event obj passed by FaaS, which includes body/headers/method/query/path
        usually you can use event_obj.body to get the POST data or event_obj.query to get the GET data
    Returns:
        json string,  {}
    """
    QUERY_STR = ""

    INPUT_VAR = ProjectConfig.request_param_input  # 从request body获取的变量

    # NOTE: 下面这一段通常不需要修改
    # parse the query data
    '''由于RedCloud框架并没有区分POST/GET，所有的请求都被转化成了GET，同时将data也放进来；与开发同学沟通，为尽可能使用便利还是会先维持现状
    所以这里无法通过method区分； 另外即使没有传参数，eventobj.body/query也不是None，所以也不能这样判断，而只能实际探测这两个数据是否有需要的值，将会优先采用data的数据，其次用query参数；
    '''
    req_json_post = {}
    req_json_query = {}
    logging.debug('body=[%s],query=[%s]' %
                  (event_obj.body.decode(), event_obj.query))
    try:    # get body data
        if event_obj.body is not None:   # body数据都会被放到这里
            postdata = parse.unquote(event_obj.body.decode())
            req_json_post = json.loads(postdata)
    except:
        pass
    try:    # get query data
        if (event_obj.query is not None) and (QUERY_STR in event_obj.query):
            # immutable dict already decoded
            querydata = event_obj.query[QUERY_STR]
            req_json_query = json.loads(querydata)
    except:
        pass

    # ===================== TODO: 在这里写你的解析和数据预处理逻辑 =====================
    input_var = {}
    for iv in INPUT_VAR:
        input_var[iv] = get_input_data_by_key_post1st(
            iv, req_json_post, req_json_query)

    # ===================== TODO: 在这里写模型处理逻辑 =====================
    try:
        input_var_processed = model.pre_process(input_var)
        predict = model.predict(input_var_processed)
        predict_formatted = model.format_predict(predict)

        return {'response': {'errorCode': 0,
                             'success': True,
                             'errorMsg': ''},
                'data': predict_formatted}
    except Exception as e:
        logging.error(f'{e}', exc_info=True)
        return {'response': {'errorCode': 500,
                             'success': False,
                             'errorMsg': str(e)}
                # ,'data':   # 确认出错时data是否需要返回，以及data默认数据类型，以免下游强类型语言服务反序列化出错
                }


def download_from_cloud():
    """
    这里实现模型从云端下载逻辑。
    当前公司sre推荐使用腾讯同步模型，这里实现了一个CosDownloader，
    可以更具实际情况实现模型同步方式，比如使用S3，则：
        s3_dlr = S3Downloader()
        s3_dlr.download()
    :return:
    """
    logging.info('downloading models from cloud... ')
    cos_dlr = CosDownloader()  # 其他下载方式需要自己实现
    cos_dlr.download()


def reload_models(event_obj):
    """
    reload model data, will be trigger by access [thisurl/-/reloaddata].
    you can create a trigger(time trigger/redis trigger/rocketmq trigger) in RedCloud to call this automatically
    """
    logging.info('loading model...')
    # 如果有传入指定模型版本(默认key='version')，则加载指定的版本
    if event_obj is not None and event_obj.body is not None:
        post_data = parse.unquote(event_obj.body.decode())
        req_json_post = json.loads(post_data)
        version = get_input_data_by_key_post1st(
            ProjectConfig.reload_version_key, req_json_post, {})
    else:
        version = None
    if version is None:
        version = ProjectConfig.model_version
    global model
    model = Model(ProjectConfig.model_path, version, ProjectConfig.model_name)
    logging.info('load model successfully')
    # TODO: 输出模型版本作为环境变量，供red-cloud平台捕捉记录

    return "reload models ok\n"


if __name__ == "__main__":
    pass
