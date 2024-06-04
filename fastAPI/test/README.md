# FastAPIのサンプル

 <br><br>

## 1.dockerのBuild方法について

+ 以下のコマンドにてbuildを実施する。
```
docker build --no-cache --tag test-fastapi:3.12-slim .
```

## 2.dockerを実行させる

+ 以下のコマンドにてdockerを実行する
```
docker run --rm --publish 8000:8000 --name app-local test-fastapi:3.12-slim
```