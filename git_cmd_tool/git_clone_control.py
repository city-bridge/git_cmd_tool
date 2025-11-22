"""git_clone_control.py - GitCloneControlクラスの実装"""

import logging
from .git_cmd import create_bare_repository, git_clone, is_git_repository, is_local_path

# ロガーの設定
logger = logging.getLogger(__name__)


class GitCloneControl:
    """
    Gitリポジトリとクローン先の関係設定を保持し、
    設定に従ってGitコマンドを管理するクラス
    """

    def __init__(self, name: str, repo_path: str, clone_path: str):
        """
        GitCloneControlインスタンスを初期化する

        Args:
            name (str): 制御オブジェクトの名前
            repo_path (str): リポジトリのパス（ローカルパスまたはURL）
            clone_path (str): クローン先のパス
        """
        self.name = name
        self.repo_path = repo_path
        self.clone_path = clone_path
        self._is_local = is_local_path(repo_path)

        logger.debug("GitCloneControl初期化: %s -> %s (name=%s)",
                     repo_path, clone_path, name)

    @property
    def is_local_repository(self) -> bool:
        """リポジトリがローカルパスかどうかを返す"""
        return self._is_local

    @property
    def repository_exists(self) -> bool:
        """リポジトリが存在するかどうかを返す"""
        if self._is_local:
            return is_git_repository(self.repo_path)
        else:
            # リモートリポジトリの場合は常にTrueとする
            # （実際の存在確認は clone 時に行われる）
            return True

    @property
    def clone_exists(self) -> bool:
        """クローン先がすでに存在するかどうかを返す"""
        return is_git_repository(self.clone_path)

    def ensure_repository(self) -> bool:
        """
        リポジトリの存在を確認し、必要に応じて作成する

        Returns:
            bool: 処理が成功した場合True

        Raises:
            Exception: 処理でエラーが発生した場合
        """
        if not self._is_local:
            # リモートリポジトリの場合は何もしない
            logger.debug("リモートリポジトリです: %s", self.repo_path)
            return True

        if self.repository_exists:
            logger.info("リポジトリは既に存在します: %s", self.repo_path)
            return True

        logger.info("bareリポジトリを作成します: %s", self.repo_path)
        return create_bare_repository(self.repo_path)

    def ensure_clone(self, force: bool = False) -> bool:
        """
        クローンの存在を確認し、必要に応じてクローンを実行する

        Args:
            force (bool): 既存のクローンを強制的に上書きするかどうか

        Returns:
            bool: 処理が成功した場合True

        Raises:
            Exception: 処理でエラーが発生した場合
        """
        if self.clone_exists and not force:
            logger.info("クローンは既に存在します: %s", self.clone_path)
            return True

        logger.info("クローンを実行します: %s -> %s", self.repo_path, self.clone_path)
        return git_clone(self.repo_path, self.clone_path, force)

    def update(self, force: bool = False) -> bool:
        """
        リポジトリとクローンの状態を更新する

        Args:
            force (bool): 既存のクローンを強制的に上書きするかどうか

        Returns:
            bool: すべての処理が成功した場合True
        """
        logger.info("更新を開始します: %s -> %s", self.repo_path, self.clone_path)

        # 1. リポジトリの確認・作成
        if not self.ensure_repository():
            return False

        # 2. クローンの確認・実行
        if not self.ensure_clone(force):
            return False

        logger.info("更新が完了しました: %s -> %s", self.repo_path, self.clone_path)
        return True

    @classmethod
    def from_dict(cls, data: dict) -> 'GitCloneControl':
        """
        辞書データからGitCloneControlインスタンスを生成する

        Args:
            data (dict): 設定データを含む辞書
                - name (str): 制御オブジェクトの名前
                - repository_path (str): リポジトリのパス
                - target_path (str): クローン先のパス
                - force_overwrite (bool, optional): 強制上書きフラグ（現在は使用せず）

        Returns:
            GitCloneControl: 生成されたGitCloneControlインスタンス
        """
        name = data.get('name')
        repo_path = data.get('repository_path')
        clone_path = data.get('target_path')

        if not name:
            raise ValueError("nameが指定されていません")
        if not repo_path:
            raise ValueError("repository_pathが指定されていません")
        if not clone_path:
            raise ValueError("target_pathが指定されていません")

        return cls(name, repo_path, clone_path)

    def to_dict(self) -> dict:
        """
        GitCloneControlインスタンスを辞書形式に変換する

        Returns:
            dict: 設定データを含む辞書
        """
        return {
            'name': self.name,
            'repository_path': self.repo_path,
            'target_path': self.clone_path,
        }

    def __str__(self) -> str:
        """文字列表現を返す"""
        return f"GitCloneControl({self.repo_path} -> {self.clone_path})"

    def __repr__(self) -> str:
        """デバッグ用の文字列表現を返す"""
        return (f"GitCloneControl(repo_path='{self.repo_path}', "
                f"clone_path='{self.clone_path}', is_local={self._is_local})")
