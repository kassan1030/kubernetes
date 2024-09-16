# VolumeBindingModeについて
- PVとPVCを作成した時やStorageClassを standardで作成したPVCは作成されてすぐにBindingされている。
- 1度も実際にPodにマウントをして利用をしていないのにPVのリソースを取ってしまっている状態
- これを実際に使うときまで(Schedulingされるまで)遅延させてくれるのがこのvolumeBindingMode
- デフォルトでは今までのように作成されてすぐにBindingする Immediateなのだが、実際にSchedulingされるまで遅延させるのが WaitForFirstConsumer

<br>

## 挙動を確認


#### 実はこの WaitForFirstConsumer と動的なProvisioningが同時に出来るボリュームタイプは現状以下の3つ。

1. AWSElacticBlockStore( kubernetes.io/aws-ebs )
1. GCEPersistentDisk( kubernetes.io/gce-pd )
1. AzureDisk( kubernetes.io/azure-disk )

<br>

> ### 設定例

+ provisonerにはkubernetes.io/no-provisonerを指定する。

```yml:storageclass.yml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: delay-bind
provisioner: kubernetes.io/no-privisioner
volumeBindingMode: WaitForFirstConsumer
```

<br>

+ StorageClassに従ったPV

```yml:persistentvolume.yml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-delay-bind
spec:
  accessModes:
  - ReadWriteOnce
  capacity:
    storage: 1Gi
  hostPath:
    path: /data/pv-delay-bind
    type: DirectoryOrCreate
  persistentVolumeReclaimPolicy: Delete
  storageClassName: delay-bind
```


<br>

+ ファイル名「storageclass.yml」「persistentvolume.yml」のマニュファエストファイルを実行

```bash:command
kubectl apply -f delay-bind.yaml -f pv-delay-bind.yaml
storageclass.storage.k8s.io/delay-bind created
persistentvolume/pv-delay-bind created 
```
<br>

+ 上記、実行後にStorageClassを請求するPVCを作成

```yml:persistentvolumeclaim.yml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pv-delay-bind-claim
spec:
  accessModes:
  - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 1Gi
  storageClassName: delay-bind
```

<br>

+ ファイル名「persistentvolumeclaim.yml」を実行

```bash:command
kubectl apply -f pv-delay-bind-claim.yaml
persistentvolumeclaim/pv-delay-bind-claim created
```

+ 下記のコマンドを実行し、PVとPVCを確認

```bash:command
$ kubectl get pv,pvc
NAME                             CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   REASON   AGE
persistentvolume/pv-delay-bind   1Gi        RWO            Delete           Available           delay-bind              61m

NAME                                        STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
persistentvolumeclaim/pv-delay-bind-claim   Pending                                      delay-bind     5s
```

<br>

+ リソースを取得するとPVのSTATUSはAvailableでまだBindingされていない。
+ PVCのほうはSTATUSがPendingになっている。
+ このように volumeBindingModeを「WaitForFirstConsumer」にするとPVCを作成しただけでは「Binding」にはならない。

<br>

#### Podのボリュームとして使うとどうなるのか確認




```yml:pod.yml
apiVersion: v1
kind: Pod
metadata:
  name: pv-delay-bind-test
spec:
  containers:
  - image: alpine
    name: alpine
    command: ["tail", "-f", "/dev/null"]
    volumeMounts:
    - name: claim-volume
      mountPath: /data
  volumes:
  - name: claim-volume
    persistentVolumeClaim:
      claimName: pv-delay-bind-claim
  terminationGracePeriodSeconds: 0
```

<br>
+ ファイル名「pod.yml」を実行

```bash:command
kubectl apply -f pv-delay-bind-test.yaml
pod/pv-delay-bind-test created
```

<br>
+ 下記のコマンドを実行し、PodとPVとPVCを確認

```bash:command
kubectl get po,pv,pvc
NAME                     READY   STATUS    RESTARTS   AGE
pod/pv-delay-bind-test   1/1     Running   0          43s

NAME                             CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                         STORAGECLASS   REASON   AGE
persistentvolume/pv-delay-bind   1Gi        RWO            Delete           Bound    default/pv-delay-bind-claim   delay-bind              67m

NAME                                        STATUS   VOLUME          CAPACITY   ACCESS MODES   STORAGECLASS   AGE
persistentvolumeclaim/pv-delay-bind-claim   Bound    pv-delay-bind   1Gi        RWO            delay-bind     6m1s
```

- PodでPVCが利用されるようになり、PVがBindingになる。
- 作成したPodが最初のConsumerとして扱われ、PVCとPVがBindingされる。


<br>

> ## 結果
>> #### 実際に利用するまでPVのBindingや動的なProvisioningであればPVの確保も遅らせることができ、リソースの節約になる。

#### 参考サイト

https://cstoku.dev/posts/2018/k8sdojo-12/