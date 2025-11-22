"""git_cmd.py - subprocessを使ってGitコマンドをラップした関数
"""

import subprocess
import logging
import shutil
from pathlib import Path
from typing import Optional

# ロガーの設定
logger = logging.getLogger(__name__)


def create_bare_repository(repo_path: str) -> bool:
    """
    ローカルにGit bareリポジトリを作成する

    Args:
        repo_path (str): 作成するbareリポジトリのパス

    Returns:
        bool: 作成に成功した場合True、失敗した場合False
    """
    repo_path_obj = Path(repo_path)

    # ディレクトリが存在しない場合は作成
    if not repo_path_obj.exists():
        repo_path_obj.mkdir(parents=True, exist_ok=True)
        logger.info("ディレクトリを作成しました: %s", repo_path)

    # 既にGitリポジトリの場合はスキップ
    if (repo_path_obj / ".git").exists() or (repo_path_obj / "HEAD").exists():
        logger.info("既存のリポジトリをスキップしました: %s", repo_path)
        return True

    # git init --bare を実行
    result = subprocess.run(
        ["git", "init", "--bare", str(repo_path_obj)],
        capture_output=True,
        text=True,
        check=True
    )

    logger.info("bareリポジトリを作成しました: %s", repo_path)
    return True


def git_clone(repo_url: str, clone_path: str, force: bool = False) -> bool:
    """
    Git cloneを実行する

    Args:
        repo_url (str): クローン元のリポジトリURL
        clone_path (str): クローン先のパス
        force (bool): 既存のディレクトリを上書きするかどうか

    Returns:
        bool: クローンに成功した場合True、失敗した場合False
    """
    clone_path_obj = Path(clone_path)

    # 既にディレクトリが存在する場合の処理
    if clone_path_obj.exists():
        if force:
            logger.warning("既存のディレクトリを削除します: %s", clone_path)
            shutil.rmtree(clone_path)
        else:
            # .gitディレクトリが存在する場合はスキップ
            if (clone_path_obj / ".git").exists():
                logger.info("既存のリポジトリをスキップしました: %s", clone_path)
                return True
            else:
                logger.warning("既存のディレクトリが存在します: %s", clone_path)
                return False

    # 親ディレクトリを作成
    clone_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # git clone を実行
    result = subprocess.run(
        ["git", "clone", repo_url, str(clone_path_obj)],
        capture_output=True,
        text=True,
        check=True
    )

    logger.info("リポジトリをクローンしました: %s -> %s", repo_url, clone_path)
    return True


def is_git_repository(path: str) -> bool:
    """
    指定されたパスがGitリポジトリかどうかを判定する

    Args:
        path (str): 判定するパス

    Returns:
        bool: Gitリポジトリの場合True、そうでなければFalse
    """
    path_obj = Path(path)

    # 通常のリポジトリ（.gitディレクトリが存在）
    if (path_obj / ".git").exists():
        return True

    # bareリポジトリ（HEADファイルが存在）
    if (path_obj / "HEAD").exists():
        return True

    return False


def is_local_path(repo_path: str) -> bool:
    """
    指定されたパスがローカルパスかどうかを判定する

    Args:
        repo_path (str): 判定するパス

    Returns:
        bool: ローカルパスの場合True、URLの場合False
    """
    # URLスキーマで始まる場合はリモート
    if repo_path.startswith(("http://", "https://", "git://", "ssh://", "git@")):
        return False

    # それ以外はローカルパスとして扱う
    return True
