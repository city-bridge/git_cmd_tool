# git cmd tool

Gitコマンドでよく使う処理をまとめる
- Pythonで実装する
- pipでインストールしてモジュールとして使用する
- Gitはコマンドで実行する

## install
```
pip install git+https://github.com/city-bridge/git_cmd_tool.git
```

## sample code
```python
from git_cmd_tool import GitCloneManager, GitCloneControl

# GitCloneManagerのインスタンスを作成
manager = GitCloneManager()

# ローカルのbareリポジトリから作業ディレクトリにクローン
manager.appendControl(GitCloneControl(
    "/path/to/bare/repo.git", 
    "/workspace/project1"
))

# GitHubリポジトリからローカルにクローン
manager.appendControl(GitCloneControl(
    "https://github.com/user/repository.git", 
    "/workspace/project2"
))

# 複数のリポジトリを一括で処理
try:
    manager.update()
    print("すべてのリポジトリの処理が完了しました")
except Exception as e:
    print(f"エラーが発生しました: {e}")
```

## 機能

### git_cmd_tool/git_cmd.py
- subprocessを使ってGitコマンドをラップした関数
  - ローカルにGit bareリポジトリの作成
  - Git clone

### git_cmd_tool/git_clone_control.py
- GitCloneControlクラスを作成
  - Gitリポジトリとクローン先の関係設定を保持
  - 設定に従ってGitコマンドを管理する
  - 機能
    - リポジトリがローカルパスの場合は、bareリポジトリ作成
    - クローン未実行の場合はクローンを実行する

### git_cmd_tool/git_clone_manager.py
- GitCloneManagerクラスの作成
  - GitCloneControlのリストを保持し、一斉に実行する

### 共通
- 結果の出力はloggingモジュールのloggerを使用する
- 例外はExceptionを使用する
