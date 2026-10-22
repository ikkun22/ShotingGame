"""実行するとステージ別ハイスコアをすべて初期化する。"""

import json
from pathlib import Path

import scores


def reset_scores(score_file=scores.SCORE_FILE):
	"""指定された保存先を空のステージ別ランキングで上書きする。"""
	empty_rankings = {str(stage): [] for stage in range(1, 4)}
	with Path(score_file).open("w", encoding="utf-8") as file:
		json.dump(empty_rankings, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
	reset_scores()
	print("ステージ1～3のハイスコアをリセットしました。")
