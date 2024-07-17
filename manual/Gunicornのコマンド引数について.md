# Gunicornのコマンド引数について

<br>

>サンプルコマンド
```bash:Command
$ gunicorn --workers=2 --bind=0.0.0.0 app.main:app
``````

## Configの設定

> Configファイルを読み込む


設定コマンド
```
-c CONFIG --config=CONFIG
```

起動コマンド例
```
$ gunicorn --config=/path/to/app/settings.py
```

## Bindの設定

>GunicornのListenポートとして待ち受けるポートを記載
>`ネットワーク:ポート`の形で指定する

設定コマンド
```
-b BIND --bind=BIND
```

起動コマンド例
```
$ gunicorn --bind=0.0.0.0:80
```
## Workers 
[公式サイトリンク](https://docs.gunicorn.org/en/stable/settings.html#workers)
>WSGIのワーカープロセス数を指定する。

設定コマンド
```
-w WORKERS --workers=WORKERS
```

起動コマンド例
```
$ gunicorn --workers=2
```

## WoekerClass
>ワーカの種類を設定する

ワーカーには大きくイカの種類がある
+ Sync Workers
 同期処理のワーカー

+ Async Workers
 非同期処理のワーカー(geventなどを利用) 

その他は下記の公式サイトで確認
[Workerの種類](https://docs.gunicorn.org/en/stable/design.html)

設定コマンド
```
-k WORAKERS --worker-class=WORKERCLASS
```

起動コマンド例
```
$ gunicorn --worker-class=sync
```


設定値は以下の通り

|値   |説明|
|:--- |:--- |
|synk | 同期設定|
|eventlet| eventlet 0.24.1が必要になります。<br>コマンド`pip install gunicorn[eventlet]`でインストールしてください|
|gevent| gevent 1.4が必要です。<br>コマンド`pip install gunicorn[gevent]`でインストールしてください|
|tornado| tornado 0.2が必要です。<br>コマンド`pip install gunicorn[tornado]`でインストールしてください|
|gthread|Python2ではfuturesパッケージをインストールする必要があります。<br>コマンド`pip install gunicorn[gthread]`でインストールしてください|



## ProcessName
>Process名を設定する

設定コマンド
```
-n APPLICATION_NAME --name APPLICATION_NAME
```

起動コマンド例
```
$ gunicorn --name=APPLICATION_NAME
```



## 参考資料

コマンドの引数
[Settings — Gunicorn 22.0.0 documentation](https://docs.gunicorn.org/en/latest/settings.html#config)

WorkerClassの説明
[Design — Gunicorn 22.0.0 documentation](https://docs.gunicorn.org/en/stable/design.html)

[gunicornのSync/Asyncワーカーの挙動を調べる #メモ - Qiita](https://qiita.com/KeisukeNagakawa/items/86d54b07defa47fd35a9)