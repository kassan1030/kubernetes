# 【Redis】Kubernetes版の構築方法

## StrageClassの登録

```yml:redis-sc.yml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: redis-local-storage
provisioner: docker.io/hostpath
volumeBindingMode: Immediate
reclaimPolicy: Retain
```

+ コマンドの実行
```Bash:command
kubectl apply -f redis-sc.yml 
storageclass.storage.k8s.io/redis-local-storage created
```
+ StorageClassが作成されていることを確認
 
```Bahs:command
kubectl get sc  
NAME                  PROVISIONER                    RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
redis-local-storage   kubernetes.io/no-provisioner   Retain          Immediate           false                  11m
```

<br>

## PersistentVolumeの登録

```yml:redis-pv.yml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: redis-db-pv
spec:
  storageClassName: redis-local-storage # StorageClassのnameを入れる。
  volumeMode: Filesystem
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: "/Users/katsushiando/Source/Github/kubernetes/redis/data" # ローカルの適当なパスを指定
    type: DirectoryOrCreate # ローカルにディレクトリがなければ作ってくれる。
```

+ コマンドの実行
```Bash:command
kubectl apply -f redis-pv.yml
persistentvolume/redis-db-pv created
```

+ PersistentVolumeが作成されていることを確認
```Bash:command
kubectl get pv
NAME          CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS          REASON   AGE
redis-db-pv   1Gi        RWO            Retain           Available           redis-local-storage            12m
```

<br>

## ConfigMapの登録

+ redisのconfファイル生成とクラスター構成のshellファイルを生成


```yml:redis-configmap.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-configmap
  labels:
    app: redis-configmap
data:
  fix-ip.sh: |
    #!/bin/sh
    CLUSTER_CONFIG="/data/nodes.conf"
    if [ -f ${CLUSTER_CONFIG} ]; then
      if [ -z "${POD_IP}" ]; then 
        echo "Unable to determine Pod IP address!"
        exit 1
      fi
      echo "Updating my IP to ${POD_IP} in ${CLUSTER_CONFIG}"
      sed -i.bak -e "/myself/ s/[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}/${POD_IP}/" ${CLUSTER_CONFIG}
    fi
    exec "$@"
  redis.conf: |+
    port 7001
    cluster-enabled yes
    cluster-require-full-coverage no
    cluster-node-timeout 15000
    cluster-config-file /data/nodes.conf
    cluster-migration-barrier 1
    appendonly yes
    protected-mode no
```

```Bash:command
kubectl apply -f redis-configmap.yml 
configmap/redis-cluster created
```


<br>

## Serviceの登録

```yml:redis-service.yml
apiVersion: v1
kind: Service
metadata:
  name: redis-cluster
  labels:
    app: redis-cluster
spec:
  ports:
  - port: 7001
    targetPort: 7001
    name: client
  - port: 17001
    targetPort: 17001
    name: gossip
  clusterIP: None
  selector:
    app: redis-pod
```


```
kubectl get service                                      
NAME            TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)              AGE
redis-cluster   ClusterIP   None             <none>        7001/TCP,17001/TCP   178m
```

+ StatefulSetと連携するサーバについて
  redis-clusterのClusterIPにIPアドレスはセットされていません。
  
+ サービス名「redis-cluster」を内部DNSで解決した場合、「エンドポイント」のIPアドレスを返します。
  
+ 以下のように、Redisクラスタのメンバー全てのIPアドレスが表示されます。
  
+ 多少無駄なトラフィックが増えますがスレーブが昇格して、マスターになって時に対応できるようにするためです。
  
  
```Bash:command
 kubectl get ep redis-cluster
NAME            ENDPOINTS                                                  AGE
redis-cluster   10.1.1.22:7001,10.1.1.23:7001,10.1.1.24:7001 + 9 more...   99s
```

+ Redis-Cluster詳細の確認コマンド

```Bash:command
katsushiando@MacBook-Pro redis % kubectl describe ep redis-cluster
Name:         redis-cluster
Namespace:    default
Labels:       app=redis-cluster
              service.kubernetes.io/headless=
Annotations:  endpoints.kubernetes.io/last-change-trigger-time: 2024-09-23T02:50:20Z
Subsets:
  Addresses:          10.1.1.22,10.1.1.23,10.1.1.24,10.1.1.25,10.1.1.26,10.1.1.27
  NotReadyAddresses:  <none>
  Ports:
    Name    Port   Protocol
    ----    ----   --------
    client  7001   TCP
    gossip  17001  TCP

Events:  <none>
```


<br>

## SatefulSetの登録

+ redisのクラスター用のPodを生成

```yml:redis-statefulset.yml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-pod
  labels:
    app: redis-pod
spec:
  serviceName: redis-pod
  replicas: 6
  selector:
    matchLabels:
      app: redis-pod
  template:
    metadata:
      labels:
        app: redis-pod
    spec:
      containers:
      - name: redis
        image: redis:5.0-rc
        ports:
        - containerPort: 7001
          name: client
        - containerPort: 17001
          name: gossip     
        command: ["/conf/fix-ip.sh", "redis-server", "/conf/redis.conf"]
        env:
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        volumeMounts:
        - name: conf
          mountPath: /conf
          readOnly: false
        - name: data
          mountPath: /data
          readOnly: false
      volumes:
      - name: conf
        configMap:
          name: redis-configmap
          defaultMode: 0755
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
      storageClassName: redis-local-storage
```


```Bash:command
kubectl apply -f redis-statefulset.yml.yml       
statefulset.apps/redis-pod created
```

```Bash:command
kubectl get StatefulSet
NAME        READY   AGE
redis-pod   6/6     138m
```

<br>

## Redis-Cluster 構築コマンドの実行

+ JsonPathにてRedis-clusterを作成する。

```Bash:command
kubectl exec -it redis-pod-0 -- redis-cli --cluster create --cluster-replicas 1 $(kubectl get pods -l app=redis-pod -o jsonpath='{range.items[*]}{.status.podIP}:7001 {end}')
```

+ Redis-cluster実行後の結果
```Bash:command
kubectl exec -it redis-pod-0 -- redis-cli --cluster create --cluster-replicas 1 $(kubectl get pods -l app=redis-pod -o jsonpath='{range.items[*]}{.status.podIP}:7001 {end}')
>>> Performing hash slots allocation on 6 nodes...
Master[0] -> Slots 0 - 5460
Master[1] -> Slots 5461 - 10922
Master[2] -> Slots 10923 - 16383
Adding replica 10.1.1.25:7001 to 10.1.1.22:7001
Adding replica 10.1.1.26:7001 to 10.1.1.23:7001
Adding replica 10.1.1.27:7001 to 10.1.1.24:7001
M: 7313822d7ffc2626432f780570e415a153d062e1 10.1.1.22:7001
   slots:[0-5460] (5461 slots) master
M: 46221d4937178427b146729b10ce22eebce08707 10.1.1.23:7001
   slots:[5461-10922] (5462 slots) master
M: 36d5122e72e40676303777c763b67af58be39ace 10.1.1.24:7001
   slots:[10923-16383] (5461 slots) master
S: fde05940f68d4aeb9a37d203fc6ef7b7a2dbe90c 10.1.1.25:7001
   replicates 7313822d7ffc2626432f780570e415a153d062e1
S: bd4a85d736631da1edf230b3c6ccfb2f1ad8635e 10.1.1.26:7001
   replicates 46221d4937178427b146729b10ce22eebce08707
S: 915da6c5732e0b76123b7859e54baae7f953b4d6 10.1.1.27:7001
   replicates 36d5122e72e40676303777c763b67af58be39ace
Can I set the above configuration? (type 'yes' to accept): yes
>>> Nodes configuration updated
>>> Assign a different config epoch to each node
>>> Sending CLUSTER MEET messages to join the cluster
Waiting for the cluster to join
...
>>> Performing Cluster Check (using node 10.1.1.22:7001)
M: 7313822d7ffc2626432f780570e415a153d062e1 10.1.1.22:7001
   slots:[0-5460] (5461 slots) master
   1 additional replica(s)
S: 915da6c5732e0b76123b7859e54baae7f953b4d6 10.1.1.27:7001
   slots: (0 slots) slave
   replicates 36d5122e72e40676303777c763b67af58be39ace
S: bd4a85d736631da1edf230b3c6ccfb2f1ad8635e 10.1.1.26:7001
   slots: (0 slots) slave
   replicates 46221d4937178427b146729b10ce22eebce08707
M: 36d5122e72e40676303777c763b67af58be39ace 10.1.1.24:7001
   slots:[10923-16383] (5461 slots) master
   1 additional replica(s)
S: fde05940f68d4aeb9a37d203fc6ef7b7a2dbe90c 10.1.1.25:7001
   slots: (0 slots) slave
   replicates 7313822d7ffc2626432f780570e415a153d062e1
M: 46221d4937178427b146729b10ce22eebce08707 10.1.1.23:7001
   slots:[5461-10922] (5462 slots) master
   1 additional replica(s)
[OK] All nodes agree about slots configuration.
>>> Check for open slots...
>>> Check slots coverage...
[OK] All 16384 slots covered.
```

<br>


## PVC,PV,SCが連結されていることを確認

+ 下記のコマンドで「PVC」「PV」「SC」の状況を表示
```Bash:command
kubectl get pvc,pv,sc                               
NAME                                     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS          AGE
persistentvolumeclaim/data-redis-pod-0   Bound    redis-db-pv                                1Gi        RWO            redis-local-storage   3h3m
persistentvolumeclaim/data-redis-pod-1   Bound    pvc-cbcfedc7-f9ff-4a6c-85fb-29cfaa7740bb   1Gi        RWO            redis-local-storage   3h3m
persistentvolumeclaim/data-redis-pod-2   Bound    pvc-46f62b92-9898-4c94-ade6-850e86770b49   1Gi        RWO            redis-local-storage   3h3m
persistentvolumeclaim/data-redis-pod-3   Bound    pvc-4a4995c9-c335-4fbc-8b7f-1bba3ba60c77   1Gi        RWO            redis-local-storage   3h3m
persistentvolumeclaim/data-redis-pod-4   Bound    pvc-1f3ec79b-0bab-4b30-87f4-fb7e39326ebf   1Gi        RWO            redis-local-storage   3h3m
persistentvolumeclaim/data-redis-pod-5   Bound    pvc-b303ba30-3a7d-493b-9182-66f0670065c0   1Gi        RWO            redis-local-storage   3h3m

NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                      STORAGECLASS          REASON   AGE
persistentvolume/pvc-1f3ec79b-0bab-4b30-87f4-fb7e39326ebf   1Gi        RWO            Retain           Bound    default/data-redis-pod-4   redis-local-storage            3h3m
persistentvolume/pvc-46f62b92-9898-4c94-ade6-850e86770b49   1Gi        RWO            Retain           Bound    default/data-redis-pod-2   redis-local-storage            3h3m
persistentvolume/pvc-4a4995c9-c335-4fbc-8b7f-1bba3ba60c77   1Gi        RWO            Retain           Bound    default/data-redis-pod-3   redis-local-storage            3h3m
persistentvolume/pvc-b303ba30-3a7d-493b-9182-66f0670065c0   1Gi        RWO            Retain           Bound    default/data-redis-pod-5   redis-local-storage            3h3m
persistentvolume/pvc-cbcfedc7-f9ff-4a6c-85fb-29cfaa7740bb   1Gi        RWO            Retain           Bound    default/data-redis-pod-1   redis-local-storage            3h3m
persistentvolume/redis-db-pv                                1Gi        RWO            Retain           Bound    default/data-redis-pod-0   redis-local-storage            3h4m

NAME                                              PROVISIONER          RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
storageclass.storage.k8s.io/redis-local-storage   docker.io/hostpath   Retain          Immediate           false                  3h19m
```

 <br>

## Redis-Cluster 構築後の構築確認コマンド

+ Redis-Clusterのendpointの確認コマンド

```Bash:command
 kubectl get ep redis-cluster
NAME            ENDPOINTS                                                  AGE
redis-cluster   10.1.1.22:7001,10.1.1.23:7001,10.1.1.24:7001 + 9 more...   99s
```

+ Redis-Cluster詳細の確認コマンド

```Bash:command
katsushiando@MacBook-Pro redis % kubectl describe ep redis-cluster
Name:         redis-cluster
Namespace:    default
Labels:       app=redis-cluster
              service.kubernetes.io/headless=
Annotations:  endpoints.kubernetes.io/last-change-trigger-time: 2024-09-23T02:50:20Z
Subsets:
  Addresses:          10.1.1.22,10.1.1.23,10.1.1.24,10.1.1.25,10.1.1.26,10.1.1.27
  NotReadyAddresses:  <none>
  Ports:
    Name    Port   Protocol
    ----    ----   --------
    client  7001   TCP
    gossip  17001  TCP

Events:  <none>
```

<br>

## Redis-Cluster 構築後の構築確認コマンド

+ Redisクライアント起動コマンド

```Bash:command
kubectl run -it redis-cli --rm --image redis --restart=Never -- bash
```

+ 既にRedisクライアント起動済みの場合はPodのコンテナで対話型シェルを起動

```Bash:command
kubectl exec -it redis-cli -- bash
```

#### Redisクライントにて動作確認


```Bash:command
kubectl run -it redis-cli --rm --image redis --restart=Never -- bash
If you don't see a command prompt, try pressing enter.

## Redisへアクセス
root@redis-cli:/data# redis-cli -c -h redis-cluster -p 7001

## Key「a」にValue「737」を代入
redis-cluster:7001> set a 737
-> Redirected to slot [15495] located at 10.1.1.24:7001
OK

## Key「b」にValue「767」を代入
10.1.1.24:7001> set b 767
-> Redirected to slot [3300] located at 10.1.1.22:7001
OK

## Key「c」にValue「777」を代入
10.1.1.22:7001> set c 777
-> Redirected to slot [7365] located at 10.1.1.23:7001
OK

## Key「d」にValue「787」を代入
10.1.1.23:7001> set d 787
-> Redirected to slot [11298] located at 10.1.1.24:7001
OK

## Key「a」のValue「737」を取得
10.1.1.24:7001> get a
"737"

## Key「b」のValue「767」を取得
10.1.1.24:7001> get b
-> Redirected to slot [3300] located at 10.1.1.22:7001
"767"

## Key「c」のValue「777」を取得
10.1.1.22:7001> get c
-> Redirected to slot [7365] located at 10.1.1.23:7001
"777"

## Key「d」のValue「787」を取得
10.1.1.23:7001> get d
-> Redirected to slot [11298] located at 10.1.1.24:7001
"787"
```


## 参考サイト

[Kubernetes StatefulSetとは？ 概要と作成方法 – Sysdig](https://sysdig.jp/learn-cloud-native/kubernetes-statefulsets-overview/)


[Redis Cluster構築時のエラーまとめ #CentOS - Qiita](https://qiita.com/ono-soic/items/d064f4db0e66249f7c85)