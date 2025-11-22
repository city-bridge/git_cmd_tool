"""git_clone_manager.py - GitCloneManagerクラスの実装"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
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
        logger.debug("GitCloneControlを追加しました: %s", control)

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
            logger.debug("GitCloneControlを削除しました: %s", control)
            return True
        except ValueError:
            logger.warning("削除対象のGitCloneControlが見つかりません: %s", control)
            return False

    def clearControls(self) -> None:
        """すべてのGitCloneControlを削除する"""
        count = len(self.controls)
        self.controls.clear()
        logger.info("%d個のGitCloneControlを削除しました", count)

    def getControls(self) -> List[GitCloneControl]:
        """
        登録されているすべてのGitCloneControlのリストを返す

        Returns:
            List[GitCloneControl]: GitCloneControlのリスト
        """
        return self.controls.copy()

    def count(self) -> int:
        """
        登録されているGitCloneControlの数を返す

        Returns:
            int: GitCloneControlの数
        """
        return len(self.controls)

    def get_control_names(self) -> List[str]:
        """
        登録されているすべてのGitCloneControlの名前リストを返す

        Returns:
            List[str]: GitCloneControlの名前のリスト
        """
        return [control.name for control in self.controls]

    def get_control_by_name(self, name: str) -> Optional[GitCloneControl]:
        """
        指定した名前のGitCloneControlを取得する

        Args:
            name (str): 取得する制御オブジェクトの名前

        Returns:
            Optional[GitCloneControl]: 見つかった場合はGitCloneControl、見つからない場合はNone
        """
        for control in self.controls:
            if control.name == name:
                return control
        return None

    def has_control_name(self, name: str) -> bool:
        """
        指定した名前の制御オブジェクトが存在するかを確認する

        Args:
            name (str): 確認する制御オブジェクトの名前

        Returns:
            bool: 存在する場合True
        """
        return any(control.name == name for control in self.controls)

    def update_by_name(self, name: str, force: bool = False) -> bool:
        """
        指定した名前のGitCloneControlのみを実行する

        Args:
            name (str): 実行する制御オブジェクトの名前
            force (bool): 既存のクローンを強制的に上書きするかどうか

        Returns:
            bool: 処理が成功した場合True

        Raises:
            ValueError: 指定した名前の制御オブジェクトが見つからない場合
        """
        control = self.get_control_by_name(name)
        if control is None:
            raise ValueError("指定した名前の制御オブジェクトが見つかりません: %s" % name)

        logger.info("名前指定で処理を開始します: %s", name)

        try:
            if control.update(force):
                logger.info("処理成功: %s", name)
                return True
            else:
                logger.error("処理失敗: %s", name)
                return False
        except Exception as e:
            logger.error("エラー発生: %s, エラー: %s", name, e)
            raise

    def load_from_json(self, json_path: str) -> int:
        """
        JSONファイルから設定を読み込む

        Args:
            json_path (str): JSONファイルのパス

        Returns:
            int: 読み込んだGitCloneControlの数
        """
        json_file = Path(json_path)
        if not json_file.exists():
            raise FileNotFoundError("JSONファイルが見つかりません: %s", json_path)

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return self.load_from_dict(data)

    def load_from_dict(self, data: Dict[str, Any]) -> int:
        """
        辞書データから設定を読み込む

        Args:
            data (Dict[str, Any]): 設定データを含む辞書
                - controls (list): GitCloneControlの設定リスト

        Returns:
            int: 読み込んだGitCloneControlの数
        """
        if 'controls' not in data:
            raise ValueError("'controls'キーが見つかりません")

        controls_data = data['controls']
        if not isinstance(controls_data, list):
            raise ValueError("'controls'はリストでなければなりません")

        loaded_count = 0
        for control_data in controls_data:
            try:
                control = GitCloneControl.from_dict(control_data)
                self.appendControl(control)
                loaded_count += 1
            except Exception as e:
                logger.error("制御オブジェクトの読み込みに失敗: %s", e)
                raise

        logger.info("%d個の制御オブジェクトを読み込みました", loaded_count)
        return loaded_count

    def save_to_json(self, json_path: str) -> None:
        """
        現在の設定をJSONファイルに保存する

        Args:
            json_path (str): 保存先JSONファイルのパス
        """
        data = self.to_dict()
        json_file = Path(json_path)
        json_file.parent.mkdir(parents=True, exist_ok=True)

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info("%d個の制御オブジェクトをJSONファイルに保存しました: %s",
                    len(self.controls), json_path)

    def to_dict(self) -> Dict[str, Any]:
        """
        GitCloneManagerの設定を辞書形式に変換する

        Returns:
            Dict[str, Any]: 設定データを含む辞書
        """
        return {
            'controls': [control.to_dict() for control in self.controls]
        }

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

        logger.info("%d個のリポジトリ処理を開始します", len(self.controls))

        success_count = 0
        error_count = 0
        errors = []

        for i, control in enumerate(self.controls, 1):
            try:
                logger.info("[%d/%d] 処理開始: %s", i, len(self.controls), control)

                if control.update(force):
                    success_count += 1
                    logger.info("[%d/%d] 処理成功: %s", i,
                                len(self.controls), control)
                else:
                    error_count += 1
                    error_msg = "[%d/%d] 処理失敗: %s" % (i,
                                                      len(self.controls), control)
                    logger.error(error_msg)
                    errors.append(error_msg)

                    if stop_on_error:
                        raise Exception("エラーにより処理を停止しました: %s" % control)

            except Exception as e:
                error_count += 1
                error_msg = "[%d/%d] エラー発生: %s, エラー: %s" % (
                    i, len(self.controls), control, e)
                logger.error(error_msg)
                errors.append(error_msg)

                if stop_on_error:
                    raise Exception("エラーにより処理を停止しました: %s" % e)

        # 結果のサマリーを出力
        logger.info("処理完了 - 成功: %d, 失敗: %d", success_count, error_count)

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
                        errors.append(
                            f"リポジトリの親ディレクトリが存在しません: {control.repo_path}")

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
