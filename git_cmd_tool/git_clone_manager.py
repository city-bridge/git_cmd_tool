"""git_clone_manager.py - GitCloneManagerクラスの実装"""

import logging
from typing import List, Optional
from .git_clone_control import GitCloneControl

# ロガーの設定
logger = logging.getLogger(__name__)


class GitCloneManager:
    """
    GitCloneControlのリストを保持し、一斉に実行するクラス
    """
    
    def __init__(self):
        """GitCloneManagerインスタンスを初期化する"""
        self.controls: List[GitCloneControl] = []
        logger.debug("GitCloneManagerを初期化しました")
    
    def appendControl(self, control: GitCloneControl) -> None:
        """
        GitCloneControlを追加する
        
        Args:
            control (GitCloneControl): 追加するGitCloneControlインスタンス
        """
        if not isinstance(control, GitCloneControl):
            raise TypeError("GitCloneControlインスタンスを指定してください")
        
        self.controls.append(control)
        logger.debug(f"GitCloneControlを追加しました: {control}")
    
    def addControl(self, repo_path: str, clone_path: str) -> GitCloneControl:
        """
        新しいGitCloneControlを作成して追加する
        
        Args:
            repo_path (str): リポジトリのパス
            clone_path (str): クローン先のパス
            
        Returns:
            GitCloneControl: 作成されたGitCloneControlインスタンス
        """
        control = GitCloneControl(repo_path, clone_path)
        self.appendControl(control)
        return control
    
    def removeControl(self, control: GitCloneControl) -> bool:
        """
        GitCloneControlを削除する
        
        Args:
            control (GitCloneControl): 削除するGitCloneControlインスタンス
            
        Returns:
            bool: 削除に成功した場合True
        """
        try:
            self.controls.remove(control)
            logger.debug(f"GitCloneControlを削除しました: {control}")
            return True
        except ValueError:
            logger.warning(f"削除対象のGitCloneControlが見つかりません: {control}")
            return False
    
    def clearControls(self) -> None:
        """すべてのGitCloneControlを削除する"""
        count = len(self.controls)
        self.controls.clear()
        logger.info(f"{count}個のGitCloneControlを削除しました")
    
    def getControls(self) -> List[GitCloneControl]:
        """
        登録されているすべてのGitCloneControlのリストを返す
        
        Returns:
            List[GitCloneControl]: GitCloneControlのリスト
        """
        return self.controls.copy()
    
    def getControlCount(self) -> int:
        """
        登録されているGitCloneControlの数を返す
        
        Returns:
            int: GitCloneControlの数
        """
        return len(self.controls)
    
    def update(self, force: bool = False, stop_on_error: bool = False) -> bool:
        """
        すべてのGitCloneControlを一斉に実行する
        
        Args:
            force (bool): 既存のクローンを強制的に上書きするかどうか
            stop_on_error (bool): エラー発生時に処理を停止するかどうか
            
        Returns:
            bool: すべての処理が成功した場合True
            
        Raises:
            Exception: stop_on_errorがTrueでエラーが発生した場合
        """
        if not self.controls:
            logger.warning("実行するGitCloneControlがありません")
            return True
        
        logger.info(f"{len(self.controls)}個のリポジトリ処理を開始します")
        
        success_count = 0
        error_count = 0
        errors = []
        
        for i, control in enumerate(self.controls, 1):
            try:
                logger.info(f"[{i}/{len(self.controls)}] 処理開始: {control}")
                
                if control.update(force):
                    success_count += 1
                    logger.info(f"[{i}/{len(self.controls)}] 処理成功: {control}")
                else:
                    error_count += 1
                    error_msg = f"[{i}/{len(self.controls)}] 処理失敗: {control}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    
                    if stop_on_error:
                        raise Exception(f"エラーにより処理を停止しました: {control}")
                
            except Exception as e:
                error_count += 1
                error_msg = f"[{i}/{len(self.controls)}] エラー発生: {control}, エラー: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
                
                if stop_on_error:
                    raise Exception(f"エラーにより処理を停止しました: {e}")
        
        # 結果のサマリーを出力
        logger.info(f"処理完了 - 成功: {success_count}, 失敗: {error_count}")
        
        if errors:
            logger.warning("以下のエラーが発生しました:")
            for error in errors:
                logger.warning(f"  - {error}")
        
        return error_count == 0
    
    def validate(self) -> List[str]:
        """
        すべてのGitCloneControlの設定を検証する
        
        Returns:
            List[str]: 検証エラーのリスト（空の場合は問題なし）
        """
        errors = []
        
        for i, control in enumerate(self.controls, 1):
            try:
                # パスの重複チェック
                for j, other_control in enumerate(self.controls, 1):
                    if i != j and control.clone_path == other_control.clone_path:
                        errors.append(f"クローン先パスが重複しています: {control.clone_path}")
                
                # ローカルリポジトリの存在チェック
                if control.is_local_repository and not control.repository_exists:
                    # 作成可能かどうかの簡単なチェック
                    from pathlib import Path
                    repo_path = Path(control.repo_path)
                    if not repo_path.parent.exists():
                        errors.append(f"リポジトリの親ディレクトリが存在しません: {control.repo_path}")
                
            except Exception as e:
                errors.append(f"検証中にエラーが発生しました: {control}, エラー: {e}")
        
        return errors
    
    def __len__(self) -> int:
        """登録されているGitCloneControlの数を返す"""
        return len(self.controls)
    
    def __str__(self) -> str:
        """文字列表現を返す"""
        return f"GitCloneManager({len(self.controls)} controls)"
    
    def __repr__(self) -> str:
        """デバッグ用の文字列表現を返す"""
        return f"GitCloneManager(controls={self.controls})"