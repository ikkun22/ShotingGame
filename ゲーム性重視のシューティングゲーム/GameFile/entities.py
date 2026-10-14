"""敵、弾、アイテムの生成処理。"""

import math
import random


def create_enemy(x, y, size, speed, enemy_type, direction, can_split=True,
				 counts_for_respawn=True):
	"""指定した位置や種類で、敵1体の状態を表す辞書を作る。"""
	return {
		"x": x,
		"y": y,
		"size": size,
		"speed": speed,
		"type": enemy_type,
		"direction": direction,
		"alive": True,
		"can_split": can_split,
		"counts_for_respawn": counts_for_respawn,
	}


def create_initial_enemies(count, size, speed, enemy_types):
	"""敵を交互の高さに並べ、種類を順番に割り当てた初期配置を作る。"""
	# 6体までは従来の間隔を使い、それ以上は画面幅に合わせて間隔を縮める
	if count <= 6:
		x_positions = [100 + index * 130 for index in range(count)]
	else:
		spacing = (800 - size - 100) / (count - 1)
		x_positions = [100 + index * spacing for index in range(count)]

	return [
		create_enemy(
		x_positions[index],
			50 + (index % 2) * 80,
			size,
			speed,
			enemy_types[index % len(enemy_types)],
			1 if index % 2 == 0 else -1,
		)
		for index in range(count)
	]


def split_enemy(enemy):
	"""分裂型の敵を、小型で分裂しない2体に分けて返す。"""
	child_size = enemy["size"] // 2
	if enemy["type"] != "splitter" or not enemy["can_split"] or child_size < 8:
		return []

	return [
		create_enemy(
			max(0, min(enemy["x"] + direction * child_size, 800 - child_size)),
			enemy["y"],
			child_size,
			enemy["speed"] * 1.5,
			"splitter",
			direction,
			False,
			False,
		)
		for direction in (-1, 1)
	]


def drop_item(items, x, y, chance, size):
	"""指定確率でアイテムを1つ選び、itemsに追加する。chanceは0から1までの確率。"""
	if random.random() < chance:
		items.append(
			{
				"x": x,
				"y": y,
				"size": size,
				"type": random.choice(("shield", "heal", "spread")),
			}
		)


def fire_bullets(bullets, x, y, is_charged, spread_shot_level, speed):
	"""発射位置から弾を追加する。強化レベルに応じて通常、3方向、5方向に撃つ。"""
	if spread_shot_level == 0:
		bullets.append([x, y, is_charged])
		return

	direction_count = 3 if spread_shot_level == 1 else 5
	for index in range(direction_count):
		angle = math.radians((index - direction_count // 2) * 15)
		velocity_x = math.sin(angle) * speed
		velocity_y = -math.cos(angle) * speed
		bullets.append([x, y, is_charged, velocity_x, velocity_y])
