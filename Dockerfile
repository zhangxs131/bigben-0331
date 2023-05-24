FROM docker-reg.devops.xiaohongshu.com/fulishe/python:3.6.15-bullseye AS build

COPY function/requirements.txt requirements.txt

RUN pip3 config set global.index-url http://pypi.xiaohongshu.com/simple/ \
    && pip3 config set global.trusted-host pypi.xiaohongshu.com \
    && pip3 install -r requirements.txt

FROM docker-reg.devops.xiaohongshu.com/fulishe/python:3.6.15-bullseye

ENV TZ Asia/Shanghai

COPY --from=build /usr/local/lib/python3.6/site-packages/ /usr/local/lib/python3.6/site-packages/

WORKDIR /home/app
COPY function/*.py ./
COPY function/dep/ .

RUN python -m compileall

RUN groupadd app && useradd -r -g app app
USER root
RUN chown -R app:app ./ 
USER app

CMD ["python3","index.py"]
