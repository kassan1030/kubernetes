# PV(PersistentVolume)
- PVは殆どが各Volumeの設定についてのフィールド

## １．accessModes
- PVのアクセスモードを指定、
- ReadWriteOnce：単一Nodeで読み書きが可能
- ReadOnlyMany：複数Nodeで読み込みが可能
- ReadWriteMany：複数Nodeから読み書きが可能

> ##### 詳細は下記サイトで確認<br><br>[リンク先](https://kubernetes.io/ja/docs/concepts/storage/persistent-volumes/#%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%83%A2%E3%83%BC%E3%83%89)

<br>

## ２．Capacity

- PVの容量を指定する
指定方法は下記のように指定するイメージ

|Key|Value|
|:--|:--|
|storage|ResourceRequirementでMemoryの容量|

> ### 記載例

```yaml:sample
capacity
  sotorage: 5Gi
```

<br>

## ３．mountOptions
- StorageClassによって動的に作成される際のマウントオプションを指定する
- このオプションはチェックされず、無効なオプションの場合単に処理が失敗する。

<br>

## ４．presistentVolumeReclaimPolicy
- StorageClassのreclaimPolicyと同様
- PVCが削除された際にPVを削除(Delete)するか、残すか(Retain)を指定する

#### デフォルトはDelete

<br>

## 5．storageClassName
- PVのStorageClassを指定する
- 空の場合どのStorageClassにも属さないPVとして扱われる

<br>

## ６．volumeMode
- PVをファイルシステム(Filesystem)として、マウントされる。
  ブロックデバイス(Block)としてマウントさせるのかを指定する。
  
#### デフォルトはFilesystem