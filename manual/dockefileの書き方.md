# DockerFileの書き方
 
 <br><br>
 
 
## Dockerfileのビルド方法

### Dockerfileのビルド 手順１
dockerfileを配置したディレクトリに移動する

```Bash:terminal
cd <dockerfileの配置してるパス>
```

### Dockerfileのビルド 手順２
ターミナルを開き、Dockerfileがあるディレクトリで以下のコマンドを実行してみます。
```Bash:terminal
docker build .
```

### Dockerfileのビルド 手順３
ビルドが終わったら以下のコマンド作成されたイメージを確認
```Bash:terminal
docker images
```

### Dockerfileのビルド 手順４
tag指定をして、buildコマンドを実施
```Bash:terminal
docker build -t python:3.12.0 .
```

### Dockerfileのビルド 手順５
Dockerコンテナを起動とコンテナの中に入る。
```Bash:terminal
docker run -it python:3.12.0 bash
```

### Dockerfileのビルド 手順６
下記のコマンドで起動を確認してみる。
```Bash:terminal
$ cat sample
#表示内容
hallo world
```
 
<br><br>
 
## Dockerfileのビルド方法



 ### ARG
 
 + 構築時にユーザが渡せる変数を定義します。
 + 変数を渡すには、構築時に`docker buid`コマンドで`--build-arg <変数名>=<値>`を指定します。
 + ユーザが構築時に引数を指定しても、Dockerfile中で指定がなければ、構築時に引数を指定しても、Dockerfileの中で指定がなければ、構築時に警告が出ます。
 
```yml:Dockerfile
 ARG <名前>[=<デフォルト値>]
```

 #### 利用例 

```yml:Dockerfile
FROM ubuntu
ARG CONT_IMG_VER
ENV CONT_IMG_VER v1.0.0
RUN echo $CONT_IMG_VER
``` 
 
 詳細はこちらの[リンク](https://docs.docker.jp/engine/reference/builder.html#arg)
 
 
 <br><br>
 
 ### FROM
+ 環境のベースを指定
+ 新しい構築ステージを初期化し、以降の命令で使うベースイメージを指定します。 
```yml:Dockerfile
 FROM [--platform=<プラットフォーム>] <イメージ名> [AS <名前>]
 FROM [--platform=<プラットフォーム>] <イメージ名>[:<タグ>] [AS <名前>]
 FROM [--platform=<プラットフォーム>] <イメージ名>[@<ダイジェスト>] [AS <名前>]
```
 
#### ARGとFROMの総合作用を理解
 + 1つ目の`FROM`命令の前に`ARG`命令があり、そこで変数が宣言されていれば`FROM`命令で参照で居ます。

 
```yml:Dockerfile
 ARG CODE_VERSION=latest
 FROM base:${CODE_VERSION}
 CMD /code/run-app
 
 FROM extras:${CODE_VERSION}
 CMD /code/run-extras
```
 
 #### 利用例
 
```yml:Dockerfile
 # FROM OSの名前：バージョン
 FROM python:3.12.0
 ```
 
```yml:Dockerfile
 # バージョン指定なし
 FROM python
 # latestのバージョンを取得します。
 ```
 
 バージョン指定しないとlatestが選択され、最新バージョンを取得します。
 
 
 <br><br>
 
 ### RUN
 イメージを作成する際、実行したいコマンドなどを記載します。
 イメージサイズを抑えるため、複数指定する場合は`&&`が推奨され舞う
 

```yml:Dockerfile
RUN <コマンド>
```

> シェル形式：コマンドはシェル内で実行される。

> デフォルトは
> Linux :/bin/sh -c
> Windows:cmd /S /C

 #### 利用例
 
```yml:Dockerfile
 # RUN　実行コマンド
 # 記載例
 RUN uptget update && uptget install -y vim
 ```
 
> 以下のFROMとRUNだけの簡単なDokcerfileをビルド,起動してみます。
>RUNには「hello world」と書かれたsampleファイルをルート直下に作成
>samplwファイルはコマンド`echo`が生成してくれます。

```Bash:terminal
 FROM python:3.12.0
 RUN echo "hello world" > sample
```

<br><br>

### CMD
+ コンテナ起動時に実行するコマンドとオプションを変更できます。
原則は末尾に記載

```yml:Dockerfile
# CMD ["実行コマンド","オプション1"."オプション2"...]
# 記載例
CMD ["ls","a"]
```

> FROMとRUNで記載したDockerfileにCMDを追記して
> 起動時に「bash」ではなく「ls -l」が実行するように変更

#### 利用例

```Bash:terminal
docker run -it ubuntu:18.04   
total 60
drwxr-xr-x   2 root root 4096 May 30  2023 bin
drwxr-xr-x   2 root root 4096 Apr 24  2018 boot
drwxr-xr-x   5 root root  360 May 31 10:33 dev
drwxr-xr-x   1 root root 4096 May 31 10:33 etc
drwxr-xr-x   2 root root 4096 Apr 24  2018 home
drwxr-xr-x   8 root root 4096 May 30  2023 lib
drwxr-xr-x   2 root root 4096 May 30  2023 media
drwxr-xr-x   2 root root 4096 May 30  2023 mnt
drwxr-xr-x   2 root root 4096 May 30  2023 opt
dr-xr-xr-x 257 root root    0 May 31 10:33 proc
drwx------   2 root root 4096 May 30  2023 root
drwxr-xr-x   5 root root 4096 May 30  2023 run
drwxr-xr-x   2 root root 4096 May 30  2023 sbin
drwxr-xr-x   2 root root 4096 May 30  2023 srv
dr-xr-xr-x  13 root root    0 May 31 10:33 sys
drwxrwxrwt   2 root root 4096 May 30  2023 tmp
drwxr-xr-x  10 root root 4096 May 30  2023 usr
drwxr-xr-x  11 root root 4096 May 30  2023 var
```

コンテナのデフォルトコマンドも`ls -l`になってます。
```Bash:terminal
CONTAINER ID   IMAGE                           COMMAND                   CREATED         STATUS                     PORTS     NAMES
233a9a84d39a   ubuntu:18.04                    "ls -l"                   3 minutes ago   Exited (0) 3 minutes ago             youthful_mendel
```

<br><br>

### WORKDIR

+ 操作するディレクトリの絶対パス(推奨)を指定します。
+ 以降はそのディレクトリを基準にDockerfileに書いた操作が実行されます。

```yml:Dockerfile
WORKDIR /path/to/workdir
```

#### 利用例

```yml:Dockerfile
 FROM python:3.12.0
 RUN mkdir sample
 WORKDIR /sample
 RUN echo "hello world" > test
```

> 記載内容詳細
>> + Dockerfileにて`sample`フォルダを作成
>> + WORKDIRを`samole`フォルダに指定
>> + RUNにてtestファイルを作成
>> + 最後にtestファイルを指定


WORKDIRの使い所は、それ以降の操作を指定したディレクトリで行きたい時などです。

<br><br>

### ENV
環境変数の設定ができます。

```yml:Dockerfile
ENV <キー>=<値> ...
```

#### 利用例

```yml:Dockerfile
# ENV 環境変数名=値
# 記載例
ENV DB_USER="user" \
    DB_PASSWORD="password" \
    DB_DATABASE="sample_db"
```

今まで作ったDockerfileに環境変数を設定してみます。
```Bash:terminal
FROM ubuntu:18.04
RUN mkdir sample
WORKDIR /sample
RUN echo "hello world" > test
ENV DB_USER="user" \
    DB_PASSWORD="password"
```

下記のコマンドにて確認可能
```Bash:terminal
docker run -it ubuntu:18.04 env
<抜粋>
DB_USER=user　←環境変数が設定される
PWD=/sample ←作業ディレクトリ(WORKDIRで指定したフォルダ)
HOME=/root
DB_PASSWORD=password　←環境変数が設定される
```

<br><br>


### COPYとADD

#### COPY
+ 追加したいファイル、ディレクトリを`<コピー元>`で指定すると、これらをイメージのファイルシステム上のパス`<コピー先>`に追加します。

```yml:Dockerfile
COPY [--chown=<ユーザ>:<グループ>] <コピー元>... <コピー先>
COPY [--chown=<ユーザ>:<グループ>] ["<コピー元>",... "<コピー先>"]
```

#### ADD
+ 追加したいファイル、ディレクトリ、リモートのファイルのURLを`<追加元>`で指定すると、こちらをイメージのファイルシステム上のパス`<追加先>`に追加します。
```yml:Dockerfile
ADD [--chown=<ユーザ>:<グループ>] <追加元>... <追加先>
ADD [--chown=<ユーザ>:<グループ>] ["<追加元>",... "<追加先>"]
```

#### 利用例

コンテナに指定したフォルダやファイルをコピーします。
使い分けとしては
+ ADD
容量が大きいファイル等をtarで圧縮した場合はADDでコピー
+ COPY
上記以外はCOPYでコピー
```yml:Dockerfile
# COPY コピー元 コピー先
# ADD コピー元 コピー先
# 記述例
COPY ./file.conf /etc/conf
ADD ./file.tar /etc/conf
```

今まで作ったDockerfileにCOPYを追記してみます
```yml:Dockerfile
FROM ubuntu:18.04
RUN mkdir sample
WORKDIR /sample
RUN echo "hello world" > test
ENV DB_USER="user" \
    DB_PASSWORD="password"
COPY ./test2 /sample
```

下記のコマンドにてCOPYを確認
```Bash:terminal
docker run -it ubuntu:18.04 ls
test  test2
```

<br><br>

### EXPOSE

```yml:Dockerfile
EXPORT <ポート>[<ポート>/<プロトコル>...]
```

#### 利用例

+ 例:TCPの指定
```yml:Dockerfile
EXPOSE 80
```
+ 例：UDPの指定
```yml:Dockerfile
EXPOSE 80/udp
```
+ 例：TCPとUDPの両方指定
```yml:Dockerfile
EXPOSE 80/tcp
EXPOSE 80/udp
```


+ コンテナの実行時、指定したネットワークポートをコンテナがリッスンするように、Dockerへ通知します。
+ 対象ポートがTCPかUDPか、どちらをリッスンするのか指定できます。
+ プロトコルの指定がなければ、TCPがデフォルトです。

<br>

> EXPORT命令だけでは、実際にはポートを公開しません

> これは、どのポートを公開する意図なのかという、イメージの作者とコンテナ実行者の両者に対し、ある種のドキュメントとして機能します。

> コンテナの実行時に実際にポートを公開するには、`docker run`で`-p`
フラグを使い、公開用のポートと割り当てるポートを指定します。



> EXPOSE関係なく、実行時に`-p`フラグを使い、その設定を上書きできます。
> 例えば以下のようにします。

```Bash:terminal
docker run -p 80:80/tcp -p 80:80/udp ...
```

<br><br>

### VOLUME

```yml:Dockerfile
VOLUME ["/data"]
```
+ VOLUME命令は、指定した名前でマウントポイントを作成します。
+ 自ホスト上や他のコンテナと行った、外部からマウントされた墓ニュームを収容する場所として、そのマウントポイントが示します。


#### 利用例

```yml:Dockerfile
FROM ubuntu:18.04
RUN mkdir myvol
RUN echo "hello world" > /myvol/test
VOLUME /myvol
```


<br><br><br>


## 参考サイト

+ 公式リファレンス
[リンク](https://docs.docker.jp/engine/reference/builder.html)

+ Dockerfileの書き方
[リンク](https://alterbo.jp/blog/ryu2-2106/)