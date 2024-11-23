FROM python:3.12.3

WORKDIR /usr/src/app

COPY . .

RUN pip install -i https://mirrors.ustc.edu.cn/pypi/web/simple pip -U \
    && pip config set global.index-url https://mirrors.ustc.edu.cn/pypi/web/simple \
    && pip install --no-cache-dir -r requirements.txt

CMD [ "python", "/usr/src/app/main.py" ]