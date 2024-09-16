# 【Kubernetes】JSONPathの書き方について

## 事前に紹介：JSONPathの初期サイト
[CheetSheet](https://kubernetes.io/docs/reference/kubectl/quick-reference/)
[JSONPathSupport]https://kubernetes.io/ja/docs/reference/kubectl/jsonpath/


<br>

## 1.文字列の扱いと式の表現

+ `-o jsonpath='<式>'`のように`'　'`で囲んで記載するのが基本の書式
+ `{}`で囲まれてない場合は、単なる文字列として扱われる

<br>

```Bash:terminal
kubectl get pod -o jsonpath='test'
```

+ 式(express)は`{}`で囲む
+ 式内部での文字列は" "で囲む
+ " "で囲まれない場合は、ルートから探索対象パスとして扱われる
+ 式として評価されると、`{"¥n"}`は改行になり、`{""¥}`はタブにになる。
+ 式は複数個並べることで連結される。

<br>

>####  `test(改行)test2(タブ)test3`にする場合は以下の記述となる<br><br>記載例

```
kubectl get pod -o jsonpath='test{"\n"}test2{"\t"}test3' 
test
test2	test3%             
```

<br>

## ２．JSONPathの探索の基本
実際は`kubectl get xxx`などの結果を元にした処理が求められる

+ JSONPathの探索は式('{ }'で囲む)で行う
+ JSONPathでデータを抽出、整形する場合
  どのような構造になってるのか確認するのが基本
  `kubectl get <pod名> -o yaml`で出力した後、データ構造を確認するといい
+ ルート(一番上)は`$1`で表すが、kubectlなどを実施する場合は特に何もしなくてもルートから始まることになっている。
  そのため、`{$.metadata.name}`は`{.metadata.name}`と書いても良い
  
<br><br>

```Bash:terminal
kubectl get pod nodejs -o yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Pod","metadata":{"annotations":{},"labels":{"app":"nodejs"},"name":"nodejs","namespace":"default"},"spec":{"containers":[{"command":["sh","-c","npm install \u0026\u0026 node -- inspect app.js"],"image":"andok10/nodejs:1.1","imagePullPolicy":"Never","name":"nodejs","ports":[{"containerPort":3000,"protocol":"TCP"}],"resources":{"limits":{"cpu":"250m","memory":"1Gi"},"requests":{"cpu":"250m","memory":"1Gi"}},"volumeMounts":[{"mountPath":"/root","name":"config"},{"mountPath":"/app","name":"application"}]}],"volumes":[{"hostPath":{"path":"/Users/katsushiando/Source/Github/kubernetes/nodejs/webapp","type":"Directory"},"name":"application"},{"hostPath":{"path":"/Users/katsushiando/Source/Github/kubernetes/nodejs/root","type":"Directory"},"name":"config"}]}}
  creationTimestamp: "2024-08-23T09:40:37Z"
  labels:
    app: nodejs
  name: nodejs
  namespace: default
  resourceVersion: "2915945"
  uid: 707d5d02-9f2c-433a-8486-1e516a0b19be
spec:
(以下省略)
```

<br>

> #### 記載例

```Bash:terminal
kubectl get pod nodejs -o jsonpath='PodName:{$.metadata.name}{"\n"}NameSpace:{$.metadata.namespace}{"\n"}'
PodName:nodejs
NameSpace:default
```

<br>

## ３．配列

+ yamlファイルの中身をコマンドで確認

```Bash:terminal
kubectl get pod nodejs -o yaml
(省略)
spec:
(省略)
tolerations:
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
(省略)
```

+ 上記は、`spec.tolerations`配下にObjectが２つ存在している
+ これはtoleration`s`のように複数形で書かれてるので配列であることが`暗示`されてる
  実際に`-`で配列要素として列挙されてます。
  
```yaml:pod.yaml
spec:
  tolerations:
  - <toleration1>
  - <toleration2>
```

<br>

> #### コマンド実行：`'{@.spce.tolerations}'` <br><br>結果

+ `[ ]`を閉じて、配列として返却する

```Bash:terminal
kubectl get pod nodejs -o jsonpath='{@.spec.tolerations}'
[
{"effect":"NoExecute","key":"node.kubernetes.io/not-ready","operator":"Exists","tolerationSeconds":300},
{"effect":"NoExecute","key":"node.kubernetes.io/unreachable","operator":"Exists","tolerationSeconds":300}
]    
```

<br>

> #### コマンド実行：`'{@.spce.tolerations[*]}'` <br><br>結果

+ `{ }`で区切って、オブジェクトとして返却する

```Bash:terminal
kubectl get pod nodejs -o jsonpath='{@.spec.tolerations[*]}'
{"effect":"NoExecute","key":"node.kubernetes.io/not-ready","operator":"Exists","tolerationSeconds":300}
{"effect":"NoExecute","key":"node.kubernetes.io/unreachable","operator":"Exists","tolerationSeconds":300}%    
```

<br>

> #### コマンド実行：`'{@.spce.tolerations[]}'` <br><br>結果

+ `'{@.spce.tolerations[]}'`は、配列の0番目を返却する

```Bash:terminal
kubectl get pod nodejs -o jsonpath='{@.spec.tolerations[]}' 
{"effect":"NoExecute","key":"node.kubernetes.io/not-ready","operator":"Exists","tolerationSeconds":300}     
```
+ `'{@.spce.tolerations[0]}'`は、配列の0番目を返却する

```Bash:terminal
kubectl get pod nodejs -o jsonpath='{@.spec.tolerations[0]}'
{"effect":"NoExecute","key":"node.kubernetes.io/not-ready","operator":"Exists","tolerationSeconds":300}   
```

<br>


## ４．ループ処理

+ 一般的には、`kubectl get pods`のように複数のオブジェクトを対象とした操作をする

> #### 例<br><br>以下の配列のデータ構成の場合

```yaml:pod.yaml
items
 - <pod1>
 - <pod2>
 - <pod3>
```

上記の構造を取得するために
JSONPathで`{.items[*].metadata.name}`と記述して実行する
Pod名が順に並んで表示される

<br>

> #### コマンド実行：`'{.items[*].metadata.name'`を実行 <br><br>結果


```Bash:terminal
 kubectl get pods -o jsonpath='{.items[*].metadata.name}'
alpine
hoge
nodej
```

<br>

### Pod名一覧：Namespace一覧を表示

> #### 失敗例<br>下記のように記載すると`Pod名一覧 + NameSpace一覧で表示される`

```Bash:terminal
kubectl get pods -o jsonpath='{.items[*].metadata.name}{.items[*].metadata.namespace}'
alpine
hoge
nodejs
default ←ここからNamespace名の一覧
default
default   
```

<br>

> #### 成功例

items配下の配列要素ごとに改行などを入れるというループ作業を行う場合
`{range}~{end}`を利用する

+ このようなプログラムを書く感じで

```c:program
for x myArrays
 x.metadata.name + " : " + x.metadata,namespace + "\n"
end if
```

+ 以下のように、`.imtems[*]`は配列を構成するオブジェクト全体に相当
  各配列要素を表す変数`x`に相当するものは`@`にて表現可能

```yaml:program
range .items[*]
  @.metadata.name + " : " + @.metadata.namespace + "\n"
```

<br>

> #### 実際にjsonpathで書くと<br>'{range .items[*]}{@.metadata.name}:{@.metadata.namespace}{"\n"}{end}' と記述する

```Bash:terminal
kubectl get pods -o jsonpath='{range .items[*]}{@.metadata.name}:{@.metadata.namespace}{"\n"}{end}' 
alpine:default
hoge:default
nodejs:default
```

<br>

> #### また、`@`をつかない場合も、自動的にそれぞれの配列要素をトップディレクトリとして扱ってくれる<br>'{range .items[*]}{.metadata.name}:{.metadata.namespace}{"\n"}{end}' と記述する

```Bash:terminal
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}:{.metadata.namespace}{"\n"}{end}'   
alpine:default
hoge:default
nodejs:default
```

<br>

> #### ループ処理は複数組み合わせることが可能であり、入れ子にすることが可能

+ コマンド
```
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}:{.metadata.namespace}{"\n"}{range @.spec.containers[*]}{@.image}{end}{end}' 
```
+ 実行内容

```Bash:terminal
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}:{.metadata.namespace}{"\n"}{range @.spec.containers[*]}{@.image}{end}{end}' 
alpine:default
alpine:latesthoge:default
andok10/python:latestnodejs:default
andok10/nodejs:1.1%   
```

<br>

## ５．フィルタリング

> #### node情報で`type=IntrnalIP`のIPアドレスを取得したい場合<br>以下のように記載する

```
kubectl get nodes -o jsonpath=`{.items[*].status.addresses[?(@.type=="InternalIP")].address}`
192.168.65.4
```

```
items
(省略)
  status:
    addresses:
    - address: 192.168.65.4
      type: InternalIP
    - address: docker-desktop
      type: Hostname
(省略)
```

+ `items[*]`となっているので、特定の配列要素だけでなく、全ての配列が対象となっている。
+ `.itmes[*].status.addresses`となっており、再び配列が存在している
  この配列addresses[0]、addresses[1]、addresses[2]....の中から、addresses["特定の条件"]という要素を`addresses[?(@.type=="InternalIP")]`の箇所で特定している。
  
+ `?`はifを表しており、if(条件式)みたいに記載は可能
+ `@`は現在の配列要素を表す
+ `.status.addresses[?(@.type=="InternalIP")]`を指定することで
  "InternalIP"を含む、配列要素のみが選択される
  この配列要素の`address`が`addresses[?(@.type=="InternalIP")].address`の対象となる
  
  
<br>

## ６．.と...は何が違うのか
[参考サイト](https://goessner.net/articles/JsonPath/)


> #### .は単なる直下のchild<br>..は直下ではなく、その下の方まで再帰的に探す。

```
kubectl get pods -o jsonpath='{.imtems[*].metadata.name}'
```

<br>


> #### は、(他に`.metadata.name`が存在しないのであれば)以下のように<br>書くことも出来るかもしてない


```
kubectl get pods -o jsonpath='{..metadata.name}'
```

<br>


## ７．ソート
```
$ kubectl get services --sort-by=.metadata.name
```

<br>

## ８．Custom-Columns

```
kubectl get pods -A -o=custom-columns='DATA:spec.containers[*].image'
kubectl get pods -A -o=custom-columns='DATA:spec.containers[?(@.image!="k8s.gcr.io/coredns:1.6.2")].image'
```

<br><br>

## 参考サイト
https://qiita.com/testnin2/items/af312b1685df37d77242
