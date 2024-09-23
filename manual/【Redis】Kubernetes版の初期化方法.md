# 【Redis】Kubernetes版の初期化方法


## 各RedisClusterのIPを確認

```Bash:command
kubectl get pod -o wide  
```

```Bash:command
get pod -o wide  
NAME          READY   STATUS    RESTARTS         AGE    IP           NODE             NOMINATED NODE   READINESS GATES
redis-pod-0   1/1     Running   0                3h9m   10.1.1.22    docker-desktop   <none>           <none>
redis-pod-1   1/1     Running   0                3h9m   10.1.1.23    docker-desktop   <none>           <none>
redis-pod-2   1/1     Running   0                3h8m   10.1.1.24    docker-desktop   <none>           <none>
redis-pod-3   1/1     Running   0                3h8m   10.1.1.25    docker-desktop   <none>           <none>
redis-pod-4   1/1     Running   0                3h8m   10.1.1.26    docker-desktop   <none>           <none>
redis-pod-5   1/1     Running   0                3h8m   10.1.1.27    docker-desktop   <none>           <none>
```

<br>

## 各RedisClusterの設定をリセットする

+ RedisClusteリセットコマンド

```Bash:command
kubectl exec -it <Pod名> -- redis-cli -p <Redisのポート番号> -h <各PodのIPアドレス> -c CLUSTER RESET
```

+ 例：Pod名「redis-cluster-0 」Redisサーバ「10.1.3.7」のポート番号「7001」をリセットする

```Bash:command
kubectl exec -it redis-cluster-0 -- redis-cli -p 7001 -h 10.1.3.7 -c CLUSTER RESET
```

<br>

## statefulsetを削除する

+ Statefulset削除コマンド

```Bash:command
 kubectl delete statefulset <statefulsetのname>
```

+ 例：Statefulset名「redis-pod」を削除する

```Bash:command
 kubectl delete statefulset redis-pod 
```

<br>

## PersistentVolumeを削除する

+ PersistentVolum削除コマンド

```Bash:command
 kubectl delete pv <PersistentVolumeのname>
```

+ 例：PersistentVolum名「redis-db-pv」を削除する

```Bash:command
kubectl delete pv redis-db-pv
```


<br>

## PersistentVolumeClaimを削除する

+ PersistentVolumClaim削除コマンド

```Bash:command
 kubectl delete pv <PersistentVolumeClaimのname>
```

+ 例：PersistentVolumClaim名「 pvc-ba02bad3-8013-42ca-88a7-aedb29647efd」を削除する

```Bash:command
kubectl delete pvc pvc-ba02bad3-8013-42ca-88a7-aedb29647efd 
```

<br>

## StorageClassを削除する

+ StorageClass削除コマンド

```Bash:command
kubectl delete sc redis-local-storage
```

+ 例：StorageClass名「redis-local-storage」を削除する

```Bash:command
kubectl delete sc redis-local-storage
```

<br>

## Serviceの削除

+ Service削除コマンド

```Bash:command
kubectl delete  service <serviceのname>
```

+ 例：Service名「redis-cluster」を削除する

```Bash:command
kubectl delete  service redis-cluster
```

<br>

## 参考コマンド


Dockerの中に入る
```
kubectl exec -it alpine /bin/ash
```

