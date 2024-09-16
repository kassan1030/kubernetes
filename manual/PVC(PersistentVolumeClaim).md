# PVC(PersistentVolumeClaim)

## １．resources
- 最低限必要なボリュームの容量を指定する
- 指定方法はResourceRequirementsとほぼ同じ

```yml:sample
resources:
  requests:
    storage: 5Gi
```

#### ここで指定した容量より、大きいPVがBindingされることもある。

<br>

## ２．selctor

- PVのBindingでLabel Selectorを利用出来る。
- Deploymentなどでも使用した matchLabelsやmatchLabelExpressionsが指定できる。

> ## PVと同様のフィールド

<br>

## １．accessModes
- PVのアクセスモードを指定、
- ReadWriteOnce：単一Nodeで読み書きが可能
- ReadOnlyMany：複数Nodeで読み込みが可能
- ReadWriteMany：複数Nodeから読み書きが可能

> ##### 詳細は下記サイトで確認<br><br>[リンク先](https://kubernetes.io/ja/docs/concepts/storage/persistent-volumes/#%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%83%A2%E3%83%BC%E3%83%89)

<br>

## 5．storageClassName
- PVのStorageClassを指定する
- 空の場合どのStorageClassにも属さないPVとして扱われる

<br>

## ６．volumeMode
- PVをファイルシステム(Filesystem)として、マウントされる。
  ブロックデバイス(Block)としてマウントさせるのかを指定する。
  
#### デフォルトはFilesystem
 
