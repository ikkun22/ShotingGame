"""ステージ別ハイスコアランキングの読み書き。"""

import json
from pathlib import Path


SCORE_FILE = Path(__file__).with_name("high_scores.json")
RANKING_LIMIT = 10


def load_scores():
	# 保存データがない場合や読み取れない場合は、空のステージ別ランキングで開始する
	try:
		with SCORE_FILE.open("r", encoding="utf-8") as score_file:
			stored_scores = json.load(score_file)
	except (OSError, json.JSONDecodeError):
		return {str(stage): [] for stage in range(1, 4)}
	if not isinstance(stored_scores, dict):
		return {str(stage): [] for stage in range(1, 4)}

	# 各ステージのデータを検査し、順位順の上位10件だけを読み込む
	rankings = {}
	for stage in range(1, 4):
		entries = stored_scores.get(str(stage), [])
		if not isinstance(entries, list):
			entries = []
		valid_entries = [
			{"name": str(entry.get("name", "PLAYER"))[:4], "score": int(entry.get("score", 0))}
			for entry in entries
			if isinstance(entry, dict) and isinstance(entry.get("score"), int)
		]
		rankings[str(stage)] = sorted(
			valid_entries, key=lambda entry: entry["score"], reverse=True
		)[:RANKING_LIMIT]
	return rankings


def qualifies(rankings, stage, score):
	entries = rankings.get(str(stage), [])
	# 10件未満なら登録でき、満員なら10位と同点以上で登録対象になる
	return len(entries) < RANKING_LIMIT or score >= entries[-1]["score"]


def add_score(rankings, stage, name, score):
	stage_key = str(stage)
	entries = rankings.setdefault(stage_key, [])
	# 新しい記録を順位順に並べ直し、上位10件をJSONへ保存する
	entries.insert(0, {"name": name[:4], "score": int(score)})
	rankings[stage_key] = sorted(
		entries, key=lambda entry: entry["score"], reverse=True
	)[:RANKING_LIMIT]
	with SCORE_FILE.open("w", encoding="utf-8") as score_file:
		json.dump(rankings, score_file, ensure_ascii=False, indent=2)