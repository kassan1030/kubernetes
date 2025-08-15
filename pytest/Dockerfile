# Dockerfile
# Pythonの公式イメージをベースにする
FROM python:3.9-alpine
USER root

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピーし、インストール
# まずrequirements.txtをコピーして依存関係をインストールすると、
# アプリケーションコードに変更があっても依存関係のレイヤーを再ビルドせずに済む
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードとテストコードをコピー
# アプリケーションコードとテストコードは同じディレクトリに置くか、
# 必要に応じて複数のCOPY命令を使う
COPY app app
COPY tests tests
COPY .coveragerc .
# pytestをデフォルトのエントリーポイントとして設定
# CMDで指定することで、Jobのcommandオーバーライドを可能にする
# 通常はここで直接テストを実行しないが、デバッグ用として残してもよい
# CMD ["pytest", "tests/"]