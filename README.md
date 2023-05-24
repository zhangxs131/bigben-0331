# readme-eccommon-redcloud

**目 录**

- [readme-eccommon-redcloud](#readme-eccommon-redcloud)
  - [背景](#背景)
  - [项目目录结构](#项目目录结构)
  - [启动](#启动)
  - [使用说明](#使用说明)
    - [流程](#流程)
    - [使用（本地访问）](#使用本地访问)

## 背景

这个工程是在 RedCloud 平台通用的模型部署服务。  
工程的目标：  

1. 提供快速的模型部署方案
2. 减少不必要的重复开发

## 项目目录结构

```shell
.
├── .gitignore              # 配置需要被git忽略的文件
├── .gitlab-ci.yml          # gitlab ci 配置文件
├── Dockerfile              # Docker 配置文件
├── README.md               # 说明
└── function                # 工程相关文件存放目录，工程根目录
    ├── models              # 模型存放位置，如果模型需要从云端下载，需要创建
    │   ├── v1              # 模型版本
    │   │   ├── model_file  # 模型文件
    ├── common.py           # 存放一些通用函数，避免循环依赖函数等
    ├── dep                 # 如果模型很小不需要通过云端转存、拉取，可存放如到这个目录
    ├── download.py         # 实现从云端下载模型
    ├── handler.py          # 服务处理业务逻辑
    ├── index.py            # 服务入口，绑定路由等
    ├── models.py           # 模型预测，数据预处理，预测后续处理等功能
    └── requirements.txt    # 依赖文件
```

## 启动

在本地启动时，cd 到工程目录（function 所在层作为根目录），安装依赖 -> 启动工程。如使用pycharm 等编译器，可在编译器中修改 project root。线上发布时不需要手动输入启动命令。

本地启动：

```shell
pip install -r requirements.txt
python index.py
```

## 使用说明

### 流程

1. 申请 cos（推荐）、aws 等桶密钥，如果模型文件过大需要通过云存储下载模型时启用，如不使用跳过此步骤。

- 申请地址（<http://dayu.devops.xiaohongshu.com/dashboard> ）具体操作联系 sre
- 找到 `config.py` 文件，在 ProjectConfig 中配置 cos 部分属性：

```python
class ProjectConfig:
    cos_secret_id = ''          # 桶 id
    cos_secret_key = ''         # 桶 key
    cos_region = ''             # 桶所在区域
    cos_bucket = ''             # 桶名称
    cos_start_prefix = ''       # 前缀
    use_cos_for_models = False  # 是否使用 cos
```

- cd 到工程根目录，执行 `mkdir -p models/v1`，创建模型存放文件夹。将模型放入其中，保持相同结构上传到云端。（可供参考： `coscmd upload -r models/ your_prefix/models/`）

2. 如果不使用云中转模型，可将模型放入 dep 文件夹。

3. 在 `config.py` 中配置模型相关属性（`model_path`,`version`,`model_name`）

4. 找到 `models.py` 文件，实现模型到相关功能，包括数据预处理，模型预测，预测结果后处理，具体说明可参见抽象基类`AbstractModel`

```python
class Model(AbstractModel):
  def predict(self, data, **kwargs):
    pass
 
  def predict_score(self, data, **kwargs):
    pass
 
  def format_predict(self, predict, **kwargs):
    pass
 
  def format_predict_score(self, predict_score, **kwargs):
    pass
 
  def pre_process(self, data_raw, **kwargs):
    pass
 
  def __init__(self, model_path, version, model_name, **kwargs):
    """
    self.model_file_path = os.path.abspath(
     os.path.join(os.path.abspath(__file__),
                  f'../{model_path}/{version}/{model_name}'))
    """
    pass
```

4. 在 config.py 中配置请求入参`request_param_input`。handler.py 中handle 是预测处理的逻辑，如果需要修改，添加额外处理逻辑，保持功能从 handle 分离。

### 使用（本地访问）

1. 健康检查：

 ```shell
 curl http://localhost:8080/_/health -d '{}' -X POST -H "Content-Type: application/json"
 ```

2. 预测, 在 `-d '{}'` 中写入 POST body：

 ```shell
 curl http://localhost:8080/ -d '{}' -X POST -H "Content-Type: application/json"
 ```

3. 重新加载模型  

 ```shell
 curl http://localhost:8080/-/reloaddata -d '{"version":"v1"}' -X POST -H "Content-Type: application/json"
 ```
