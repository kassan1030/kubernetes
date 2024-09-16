# SC(StorageClass)

## １．provisioner

- Provisionerを指定する
  - kubernetes.io/gce-pd 
  - kubernetes.io/aws-ebs
  - kubernetes.io/glusterfs

> #### 詳細は下記サイトで確認<br><br>[リンク先_Provisonerについて](https://kubernetes.io/docs/concepts/storage/storage-classes/#provisioner)
 
<br>

## ２．parameters

- ProvisonerのパラメータをKey/Value形式で指定する

> #### 詳細は下記サイトで確認<br><br>[リンク先_parametersについて](https://kubernetes.io/docs/concepts/storage/storage-classes/#parameters)


<br>


## ３．reclaimPolicy

- PVCが削除された際にPVを削除(Delete)するか、残すか(Retain)を指定する

#### デフォルトはDelete

<br>

## ４．volumeBindingMode
- PVCが作成された際に、即時にPVを紐づけるか(Immediate)、実際に使用される際に紐づけるか(WaitForFirstConsumer)を指定する
- WaitForFirstConsumerだと、PVCが生成された際には、まだPVが生成されたりBindされたりしない。
- PVCが実際にPodで利用される際に作成・Bindingが行われるようになる

<br>

## ５．mountOptions
- StorageClassによって動的に作成される際のマウントオプションを指定する
- このオプションはチェックされず、無効なオプションの場合単に処理が失敗する。

<br>

## ６．allowVolumeExpansion

- ボリュームの拡張を許可するかを指定

#### デフォルトはFalse

<br>

## ７．allowedTopologies

- 動的にプロビジョニングする際の対象Nodeを制限することが出来る
- matchLabelExpressionsでNodeのトポロジーを指定する