
# 【DockerDesktop】KubernetesがStartingで動かない対応方法


## DockerDesktopを完全にアンインストール


<br>

### 対処１.Kubernetesが「Starting」で止まらない場合

> #### 以下のコマンドでDockerDesktopをアンインストールします。

+ DockerDesktop アンインストール方法

```shell:Command
/Applications/Docker.app/Contents/MacOS/uninstall
```

<br>
<br>


### これだけでは、KubernetesのStartingが続くのは直らない

### 対処２.残存ファイルを削除する(完全削除のため推奨手順)



> Docker Desktop は、アンインストールしても一部の関連ファイルやキャッシュが残ることがあります。<br>これらを削除することで、完全にクリーンな状態にできます。

<br>


#### 手順１．DockerDesktopを終了

Docker Desktop を終了します。
(メニューバーの Docker アイコンをクリックし、「Quit Docker Desktop」を選択)



#### 手順２．ターミナルを開きます。

以下のコマンドを一つずつ実行し、Docker に関連するファイルを削除します。

<br>

#### 手順３．Docker のキャッシュディレクトリを削除:

```shell:Bash
rm -rf ~/Library/Caches/com.docker.docker
```

<br>

#### 手順４．Docker のグループコンテナを削除:

```shell:Bash
rm -rf ~/Library/Group\ Containers/group.com.docker
```

<br>

#### 手順５．Docker のコンテナ関連ファイルを削除:

```shell:Bash
rm -rf ~/Library/Containers/com.docker.docker
```

<br>

#### 手順６．Docker の設定ファイルを削除:

```shell:Bash
rm -rf ~/Library/Preferences/com.docker.docker.plist
rm -rf ~/Library/Preferences/com.electron.docker-frontend.plist
```

<br>

#### 手順７．Docker のログファイルを削除:

```shell:Bash
rm -rf ~/Library/Logs/Docker\ Desktop
```

<br>

#### 手順８．保存されたアプリケーション状態を削除:

```shell:Bash
rm -rf ~/Library/Saved\ Application\ State/com.electron.docker-frontend.savedState
```

<br>

#### 手順９．docker ディレクトリを削除:

```shell:Bash
rm -rf ~/.docker
```

<br>

#### 手順１０．VMnetd 関連ファイルを削除 (パスワードの入力が必要な場合があります):

```shell:Bash
sudo rm -f /Library/LaunchDaemons/com.docker.vmnetd.plist
sudo rm -f /Library/PrivilegedHelperTools/com.docker.vmnetd
```

<br>

#### 手順１１．Docker アプリケーション自体を完全に削除:

```shell:Bash
sudo rm -rf /Applications/Docker.app
```


<br><br>
