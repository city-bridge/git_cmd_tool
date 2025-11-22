# git cmd tool

Gitコマンドでよく使う処理をまとめる
- Pythonで実装する
- pipでインストールしてモジュールとして使用する
- Gitはコマンドで実行する

## install
```
pip install git+https://github.com/city-bridge/git_cmd_tool.git
```

## 使用方法

### sample code
```python
from git_cmd_tool import GitCloneManager, GitCloneControl

# GitCloneManagerのインスタンスを作成
manager = GitCloneManager()

# ローカルのbareリポジトリから作業ディレクトリにクローン
manager.appendControl(GitCloneControl(
    "project1",
    "/path/to/bare/repo.git", 
    "/workspace/project1"
))

# GitHubリポジトリからローカルにクローン
manager.appendControl(GitCloneControl(
    "project2",
    "https://github.com/user/repository.git", 
    "/workspace/project2"
))

# JSON設定ファイルからの読み込み
try:
    manager.load_from_json("config.json")
    print(f"JSON設定から{manager.count()}個の制御オブジェクトを読み込み")
except Exception as e:
    print(f"JSON読み込みエラー: {e}")

# 辞書データからの直接読み込み
config_dict = {
    "controls": [
      {
        "name": "project3",
        "repository_path": "/path/to/repo/project3",
        "target_path": "/release/project3"
      }
    ]
}
manager.load_from_dict(config_dict)
print(f"辞書設定から{manager.count()}個の制御オブジェクトを読み込み")

# 名前による制御オブジェクトの管理
print(f"登録された制御オブジェクト名: {manager.get_control_names()}")
print(f"総制御オブジェクト数: {manager.count()}")

# 名前で制御オブジェクトを取得
control = manager.get_control_by_name("project1")
if control:
    print(f"'project1'制御オブジェクト: {control}")

# 名前の存在確認
exists = manager.has_control_name("project1")
print(f"'project1'の存在: {exists}")

# 複数のリポジトリを一括で処理
try:
    # 特定の名前のみ実行
    manager.update_by_name("project1")
    print("メインプロジェクトのチェックアウトが完了")

    manager.update()
    print("すべてのリポジトリの処理が完了しました")
except Exception as e:
    print(f"エラーが発生しました: {e}")
```

### JSON設定ファイル例
```json
{
  "controls": [
    {
      "name": "main_project",
      "repository_path": "ssh://git.example.com/repo/project.git",
      "target_path": "/workspace/project1"
    },
    {
      "name": "project1",
      "repository_path": "/path/to/repo/project1",
      "target_path": "/release/project1-v1.0",
      "force_overwrite": true
    }
  ]
}
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
