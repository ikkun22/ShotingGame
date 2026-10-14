"""ステージごとのゲーム内容をまとめた設定。"""

import settings


# ステージごとの初期敵数と、ボス出現までに必要な撃破数
STAGE_CONFIGS = {
	1: {
		"enemy_count": settings.ENEMY_COUNT,
		"boss_defeat_count": 50,
		"boss_uses_damage_bounce_attack": False,
		"boss_spread_shot_interval": 1000,
		"boss_spread_shot_interval_decrease": 100,
		"boss_spread_shot_interval_min": 300,
	},
	2: {
		"enemy_count": settings.ENEMY_COUNT,
		"boss_defeat_count": 50,
		"enemy_types": ("horizontal", "diving", "splitter"),
		"boss_uses_spread_attack": False,
		"boss_bounce_shot_interval": 1000,
	},
	3: {
		"enemy_count": settings.ENEMY_COUNT,
		"boss_defeat_count": 50,
		"enemy_types": settings.ENEMY_TYPES + ("horizontal", "diving", "splitter"),
	},
}
