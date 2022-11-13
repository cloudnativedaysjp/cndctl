class Cli:
    def __init__(self) -> None:
        pass

    def accept_continue(self, message: str) -> bool:
        """Y/Nプロンプトを出力して入力結果に応じてBoolを返す

        Args:
            message (str): プロンプトに出力する文字列を指定

        Returns:
            bool: Y押下でTrue、それ以外でFalseを返す
        """
        while True:
            choice = input(f"{message.lower}\n continue? [y/n] :")
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
