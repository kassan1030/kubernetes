# WorkerClassについて

### Master
マスタープロセスは
さまざまなプロセスシグナルをリッスンし、それに応じて反応する単純なループです。
`TTIN,TTOI,CHLD`などのシグナルをリッスンして、実行中のワーカリストを管理します。

|シグナル|説明|
|:--|:--|
|TTIN,TTOU|実行中のワーカーの数を増やすか、減らすように指示します。|
|CHILD|子プロセスが終了した事を示し、この場合は!`マスタープロセス`は`失敗したワーカーを自動的に再起動します。`|

### Sync Workers
もっとも基本的でデフォルトのワーカータイプ
`1度に１つのリクエスト処理`する同期ワーカークラスです。

このモデルは、エラーが最大１つのリクエストにしか影響しないため、最も簡単に理解できます。

ただし、以下のように
１度に１つのリクエストのみを処理するには、アプリケーションのプログラミングでいくつかの仮説を
用いて実装することが必要です。

>`sync`ワーカーは永続的な接続をサポートしてません。
>>応答が送信された後、各接続は閉じられます。
>>アプリケーションヘッダーに`keep-alive`を以下のように設定した場合も
```
Connection:keep-alive
```

### Async Workers
非同期のワーカーは
[Greenlet](https://github.com/python-greenlet/greenlet)に基づいています。

[Eventlet](https://eventlet.readthedocs.io/en/latest/)
[gevent](https://www.gevent.org/)

Greenletは、Pythonの協調型マルチスレッドの実装です。
一般にアプリケーションはこれからのワーカークラスを変更せずに使用できるはずです。

完全なgreenletサポートをするためには、アプリケーションを調整する必要があるかもしれません。
例えば

[gevent](https://www.gevent.org/)
[Psycopg](https://github.com/psycopg/psycogreen/)

がインストールされ、[設定](https://www.gevent.org/api/gevent.monkey.html#plugins)
されているこを確認してください。

他のアプリケーションは
例えば、パッチが適用されていない元の動作にいぞんしているため
まったく互換性がない可能性があります。

### Gthread Workers
GthreadWorker
メインループで接続を受け入れます。
受け入れられた接続は、接続ジョブとしてスレッドプールに追加されます。
`KeepAlive`では、接続はループに戻され、イベント待機します。
`KeepAlive timeout`後にイベントが発生しない場合、接続は閉じられます

### Tornado Workers
Tornado Workers
これを使用して、Tornadoフレームワークを使用してアプリケーションを作成できます。
`Tornado Wokers`はWSGIアプリケーションを提供できますが、これは推奨される構成はありません。

### AsyncIO Workers
これらのワーカーはPython3と互換性があります。

アプリケーションを移植して[aiohttp's](https://docs.aiohttp.org/en/stable/deployment.html#nginx-gunicorn)の
`web.Application`APIを使用し、`aiohttp.worker.GunicornWebWorker`ワーカーを使用することもできます。


## Workers Typeの選択
デフォルトの`Sync Workers`は
アプリケーションがCPUとネットワーク帯域幅の点でリソースバウンドされてる事を前提としています。

一般的に、これはアプリケーションが、不定の時間を要する処理を実行すべきではないことを意味します。
不定の時間を要する処理として

インターネットへのリクエストが挙げられます。
ある時点で外部ネットワークに障害が発生し、クライアントがサーバに大量アクセスします。
したがって、APIへの送信リクエストを行うWebアプリケーションは、`Async Workers`の恩恵を受けます。

このリソース制御の想定は、デフォルト構成のGunicornの前に`buffering proxy`が必要になります。
`Sync Workers`をインターネット公開すると、サーバにデータを少しづつ流す負荷を作成することで
DOS攻撃が簡単に実行できるようになります。

>例
HeyはWeb アプリケーションに負荷を送信する小さなプログラム

[Hey GitHub](https://github.com/rakyll/hey)

`Async Workers`を必要とする動作の例をいくつか示します。

+ Applications making long blocking calls　(外部Webサービスなど)
(長時間のブロッキング呼び出しを行うアプリケーション)

+ Serving requests directly to the internet

+ Streaming requests and responses

+ Long polling

+ Web sockets

+ Comet

>Comet
>> コメットを利用したWebアプリケーションでは
>> Ajaxを利用してサーバへリクエストを発行すると、即座にレスポンスを返すのではなく
>> サーバ上でリクエストを保持する。
>> 
>> 保持されたリクエストはサーバ上で何らかのイベントが発生したときにレスポンスとして返される。



## How Many Workers?
予想されるクライアント数に合わせてワーカ数を拡張しないでください

Gunicornでは、1秒あたり数百または数千のリクエストを処理するのに4~12のワーカープロセスが必要です。
Gunicornは、リクエスト処理する際にすべての負荷分散をOSに依存してます。

一般的に、開始時のWorkers数は`(2 x $num_cores) + 1`をおすすめします。

この式は、特定のコアでは、１つのワーカーがソケットから読み取りまたは書き込みを行い
もう１つの`Workers`がリクエストを処理するという仮定に基づいています。

当然のことながら
特定のハードウェアとアプリケーションは、最適なWorkers数に影響します。

まずは、上記の推測から始めて
アプリケーションに負荷が掛かっているときに`TTIN`および`TTOUT`信号を使用して
調整することをおすすめします。

`Workers`が多すぎるということもあるという事を常に覚えておいてください。
`Workers Process`がシステムリソースを大量に消費し始め、システム全体のスループットが低下します。

## How Many Threads?
Gunicorn19以降、`Threads Option`を使用して、複数のスレッドでリクエスト処理出来ます。
`Threads`を使用すると、`gthread Woekers`の使用が前提となります。

スレッドの利点の１つは
リクエストが`Workers Timeout`より長くかかる可能性があり
`Master Process`がフリーズしてないので強制終了ないように通知することが出来ることです。

システムによっては
複数の`Threads`、複数の`WorkersProcess`またはその組み合わせを使用すると
最良の結果が得られる場合があります。

例えば、`CPython`がスレッド使用する場合
スレッドの実装がそれぞれ異なるため、`Jython`ほどのパフォーマンスが得られない可能性があります。

Processの代わりにThreadsを使用すると、Gunicornの`Memory footprint`を削減しながら
`leload`シグナルを使用してアプリケーションのアップグレードを行うことが出来ます。

`ApplicationCode`は`Workers`間で共有されますが、`WorkerProcess`のみロードされる。
(CodeをMasterProcessにロードする`preload`設定をする場合とは異なります。)


>>Memory footprint(メモリーフットプリント)
>プログラムが実行中に使用または参照するメインメモリの合計量を意味する

##参考資料


[Design — Gunicorn 22.0.0 documentation](https://docs.gunicorn.org/en/stable/design.html)

[gunicornのSync/Asyncワーカーの挙動を調べる #メモ - Qiita](https://qiita.com/KeisukeNagakawa/items/86d54b07defa47fd35a9)