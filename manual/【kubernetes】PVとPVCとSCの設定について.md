# PVとPVCとSCの設定について


## StorageClassの定義

+ LocalVolumeに対応したStorageClassをマニュフェストファイルに定義

```yaml:sc.yml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: local-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
```

+ provisonerはDynamic Provisioningが非サポートとのため、`kubernetes.io/no-provisioner`を指定します
+ volumeBindingModeは、`WaitForFirstConsumer`を設定することで、実際にPodにVolumeが割り当てられるまでVolumeを使用しないようになります。

<br>

## PersistentVolumeの定義

 + PersistentVolumeのマニュフェストファイルを作成

```yaml:pv.yml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-storage
  local:
    path: /mnt/disks/vol1
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - k8s-node1
```

+ spec.accessModesは、Localvolumeの他のPodから共有で利用することが出来ず、
  １つのPodからしかRead/Writeが出来ないため、ReadWriteOnceを指定します。
+ persistentVolumeReclaimPolicyは、PersistentVolumeClaimが削除された時のデータ削除のポリシーを指定できます。
LocalVolumeの場合は`Retain`を指定してください

persistentVolumeReclaimPolicyにはデータを削除する`Recycle`、Volumeを同時に削除するDeleteが指定可能です。

しかし、`Recyle`はデータを削除するのであれば、そもそもLocalVolumeを使う理由もありませんし、`Delete`はDynamicProvisioningが非サポートのため、指定してもPersistentVolumeClaimされるとPersistetVolumeのステータスがFAILになります。

+ storageClassNameは、先ほどデプロイしたStorageClassのnameの`local-storage`を指定します。

+ spec.local.pathは、LocalVolumeの準備で作成したディレクトリ`/mnt/disks/vol1`を指定します。

+ nodeAffinityは、どのNodeを使うのかの条件を指定します。
  今回は、Nodeの`k8s-node1`のみ選択されるように`kubernetes.io/hostname`をキーとして指定しています。
  

## PersistentVolumeClaim の定義

 + PersistentVolumeClaimのマニュフェストファイルを作成
 
```yaml:pvc.yml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: local-claim
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: local-storage
  resources:
    requests:
      storage: 1Gi
```

+ spec.storageClassNameには、先に定義したStorageClassのnameである`local-storage`を指定します。

<br>

## LocalVolumeを使ったPodの定義

+ PersistentVolumeClaimの`local-claim`を使い、PodへLocalvolumeを割り当てます。

```yaml:pod.yml
apiVersion: v1
kind: Pod
metadata:
  name: my-nginx-pod
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
    - containerPort: 80
    volumeMounts:
    - mountPath: "/usr/share/nginx/html"
      name: mydata
  volumes:
    - name: mydata
      persistentVolumeClaim:
        claimName: local-claim
```


+ spec.containers.volumeMounts,mountPathに、Pod内のLocalVolumeのマウント先を指定します。
+ spec.volumes.persistentVolumeClaimに、先に定義したPersistentVolumeClaimのnameである`local-claim`を指定します。




## 参考資料

[Kubernetes: Local Volumeの検証 #kubernetes - Qiita](https://qiita.com/ysakashita/items/67a452e76260b1211920)