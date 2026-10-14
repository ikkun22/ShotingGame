"""ゲーム中の敵移動ルール。"""

import math


def create_boss_bullet(
	boss_x, boss_y, target_x, target_y, speed, created_at, angle_offset_degrees=0
):
	"""角度オフセットを付けたボス弾を作り、[位置、速度、作成時刻]を返す。"""
	direction_x = target_x - boss_x
	direction_y = target_y - boss_y
	distance = math.hypot(direction_x, direction_y)
	if distance == 0:
		direction_x, direction_y, distance = 0, 1, 1
	angle = math.atan2(direction_y, direction_x) + math.radians(angle_offset_degrees)
	return [
		boss_x,
		boss_y,
		math.cos(angle) * speed,
		math.sin(angle) * speed,
		created_at,
	]


def move_bouncing_bullets(bullets, screen_width, screen_height, current_time, lifetime, radius=5):
	"""期限切れの弾を除き、残った弾を移動して画面の端で反射させる。"""
	bullets[:] = [
		bullet for bullet in bullets if current_time - bullet[4] < lifetime
	]
	for bullet in bullets:
		bullet[0] += bullet[2]
		bullet[1] += bullet[3]
		if bullet[0] < radius:
			bullet[0] = radius
			bullet[2] = abs(bullet[2])
		elif bullet[0] > screen_width - radius:
			bullet[0] = screen_width - radius
			bullet[2] = -abs(bullet[2])
		if bullet[1] < radius:
			bullet[1] = radius
			bullet[3] = abs(bullet[3])
		elif bullet[1] > screen_height - radius:
			bullet[1] = screen_height - radius
			bullet[3] = -abs(bullet[3])


def move_enemies(enemies, player_x, player_y, screen_width):
	"""生存中の敵を種類に応じて移動させる（追跡、直進、左右に揺れる動き）。"""
	for enemy in enemies:
		if not enemy["alive"]:
			continue

		if enemy["type"] == "chaser":
			distance_x = player_x - (enemy["x"] + enemy["size"] / 2)
			distance_y = player_y - (enemy["y"] + enemy["size"] / 2)
			distance = math.hypot(distance_x, distance_y)
			if distance > 0:
				enemy["x"] += distance_x / distance * enemy["speed"]
				enemy["y"] += distance_y / distance * enemy["speed"]
		elif enemy["type"] == "straight":
			enemy["y"] += enemy["speed"]
		elif enemy["type"] == "horizontal":
			enemy["x"] += enemy["direction"] * enemy["speed"] * 2
			enemy["y"] += enemy["speed"] * 0.5
			if enemy["x"] <= 0 or enemy["x"] >= screen_width - enemy["size"]:
				enemy["x"] = max(0, min(enemy["x"], screen_width - enemy["size"]))
				enemy["direction"] *= -1
		elif enemy["type"] == "diving":
			distance_x = player_x - (enemy["x"] + enemy["size"] / 2)
			enemy["x"] += max(-enemy["speed"], min(distance_x, enemy["speed"]))
			enemy["y"] += enemy["speed"] * 2.5
		elif enemy["type"] == "splitter":
			enemy["x"] += enemy["direction"] * enemy["speed"]
			enemy["y"] += enemy["speed"]
			if enemy["x"] <= 0 or enemy["x"] >= screen_width - enemy["size"]:
				enemy["x"] = max(0, min(enemy["x"], screen_width - enemy["size"]))
				enemy["direction"] *= -1
		else:
			enemy["y"] += enemy["speed"]
			enemy["x"] += enemy["direction"] * enemy["speed"] * 2
			if enemy["x"] <= 0 or enemy["x"] >= screen_width - enemy["size"]:
				enemy["direction"] *= -1
