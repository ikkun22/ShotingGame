# 数学計算、敵の出現位置のランダム決定、ゲーム画面の作成に使うモジュールを読み込む
import math
import random
import sys
import pygame
import audio
import settings
import entities
import ui
import game as game_logic
import stages
import scores as score_storage

# pygameを使うための初期設定を行う
pygame.init()
audio_manager = audio.AudioManager()

# 800×600のゲーム画面を作成し、タイトルと文字のフォントを設定する
screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
pygame.display.set_caption("2D Shooting")
font = pygame.font.Font(None, 32)
clock = pygame.time.Clock()

# ==================================================
# ゲーム開始時の初期設定
# プレイヤー、弾、敵、HP、スコアなどの最初の状態を設定する
# ==================================================
# プレイヤーの初期位置と移動速度を設定する
# player_speedを大きくするとプレイヤーが速く移動する
player_x = settings.PLAYER_START_X
player_y = settings.PLAYER_START_Y

player_speed = settings.PLAYER_SPEED

# プレイヤーの大きさを設定する
player_width = settings.PLAYER_WIDTH
player_height = settings.PLAYER_HEIGHT

# 発射した弾を保存するリストと、弾の移動速度を設定する
bullets = []
bullet_speed = settings.BULLET_SPEED

# 敵を倒したときに落ちるアイテムを管理する
items = []
item_drop_chance = settings.ITEM_DROP_CHANCE
item_size = settings.ITEM_SIZE
item_speed = settings.ITEM_SPEED
player_shielded = False
spread_shot_level = 0

# 選択中のステージと、そのステージの設定を読み込む
selected_stage = 1
stage_config = stages.STAGE_CONFIGS[selected_stage]
boss_defeat_count = stage_config["boss_defeat_count"]
boss_shot_interval = stage_config.get("boss_spread_shot_interval", 1000)
# 敵の数、大きさ、移動速度を設定する
enemy_count = stage_config["enemy_count"]
enemy_size = settings.ENEMY_SIZE
enemy_speed = settings.ENEMY_SPEED
# chaser: プレイヤーを追いかける敵
# straight: 下へまっすぐ進む敵
# zigzag: 左右に動きながら下へ進む敵
enemy_types = stage_config.get("enemy_types", settings.ENEMY_TYPES)
# 敵の位置や生存状態を辞書に保存し、敵のリストを作成する
enemies = entities.create_initial_enemies(enemy_count, enemy_size, enemy_speed, enemy_types)
# プレイヤーの生存状態、HP、撃破数を管理する
player_alive = True
player_hp = settings.PLAYER_MAX_HP
score = 0
enemies_defeated = 0
boss = None
boss_bullets = []
boss_bounce_bullets = []
boss_hp = settings.BOSS_INITIAL_HP
boss_respawn_at = None
# 敵を倒した数に応じて、上から敵を1体追加する
respawn_interval = settings.ENEMY_RESPAWN_INTERVAL
respawn_progress = 0
next_respawn_count = respawn_interval
# ゲームオーバーの判定、プレイヤーが倒されてからゲーム終了までの時間を設定する
player_dead_time = None
game_over_delay = settings.GAME_OVER_DELAY
# 被弾後の無敵時間に使う値を設定する
player_invincible_until = 0
blink_duration = settings.PLAYER_BLINK_DURATION
# ゲーム画面の色を反転するかどうかを管理する
color_inverted = False
# チャージショットの状態を管理する
charge_start_time = None
charge_time_required = settings.CHARGE_TIME_REQUIRED


def game_color(color):
	return ui.game_color(color, color_inverted)



def create_boss_bounce_shots(boss, target_x, target_y, speed, created_at, single_shot=False):
	# ステージ2ではHP半分以下になると、狙い角の左右15度へ分けて撃つ
	angle_offsets = (
		(-15, 15)
		if not single_shot
		and stage_config.get("boss_bounce_shot_interval") is not None
		and boss["hp"] <= boss["max_hp"] / 2
		else (0,)
	)
	return [
		game_logic.create_boss_bullet(
			boss["x"],
			boss["y"] + boss["size"] / 2,
			target_x,
			target_y,
			speed,
			created_at,
			angle_offset_degrees,
		)
		for angle_offset_degrees in angle_offsets
	]


# メニュー画面に表示するタイトルとボタンの設定
title_font = pygame.font.Font(None, 64)
# 日本語を表示できるフォントを設定する
menu_font = pygame.font.SysFont("yugothic", 40)
button_font = pygame.font.SysFont("yugothic", 30)
start_button = pygame.Rect(150, 300, 200, 60)
exit_button = pygame.Rect(450, 300, 200, 60)
# STARTとEXITの下に表示するCUSTOMボタン
custom_button = pygame.Rect(150, 400, 200, 60)
stage_buttons = [
	pygame.Rect(60 + index * 240, 280, 180, 80)
	for index in range(len(stages.STAGE_CONFIGS))
]
stage_back_button = pygame.Rect(20, 20, 140, 50)
score_button = pygame.Rect(450, 400, 200, 60)
score_table_stage_buttons = [
	pygame.Rect(150 + index * 180, 100, 150, 50)
	for index in range(len(stages.STAGE_CONFIGS))
]
score_table_back_button = pygame.Rect(330, 535, 140, 45)
# 起動時に保存済みのステージ別ランキングを読み込む
high_scores = score_storage.load_scores()

# ==================================================
# 設定画面で使う初期値
# 「初期設定に戻す」を選んだとき、ここで指定した値に戻る
# ==================================================
default_player_speed = settings.DEFAULT_PLAYER_SPEED
default_bullet_speed = settings.DEFAULT_BULLET_SPEED
default_enemy_speed = settings.DEFAULT_ENEMY_SPEED

# CUSTOM画面の速度設定
# 各速度は「左矢印で減少、右矢印で増加」し、ここで指定した範囲に収まる
# minは設定できる最小値、maxは設定できる最大値、stepは1回の変更量
enemy_speed_min = settings.ENEMY_SPEED_MIN
enemy_speed_max = settings.ENEMY_SPEED_MAX
enemy_speed_step = settings.ENEMY_SPEED_STEP
player_speed_min = settings.PLAYER_SPEED_MIN
player_speed_max = settings.PLAYER_SPEED_MAX
player_speed_step = settings.PLAYER_SPEED_STEP
bullet_speed_min = settings.BULLET_SPEED_MIN
bullet_speed_max = settings.BULLET_SPEED_MAX
bullet_speed_step = settings.BULLET_SPEED_STEP

# ==================================================
# メニュー画面の処理
# 弾をSTART、EXIT、CUSTOMに当てて画面を移動する
# ==================================================
def show_menu():
	global player_x, player_y, bullets, enemies, enemy_speed, selected_stage
	global stage_config, enemy_count, enemy_types, boss_defeat_count, boss_shot_interval

	# STARTが選ばれるまでメニュー画面を表示する
	menu_running = True
	while menu_running:
		frame_scale = clock.tick(60) / (1000 / 60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				bullets.append([player_x, player_y])

		# メニュー画面でも矢印キーでプレイヤーを移動させる
		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT]:
			player_x -= player_speed * frame_scale
		if keys[pygame.K_RIGHT]:
			player_x += player_speed * frame_scale
		if keys[pygame.K_UP]:
			player_y -= player_speed * frame_scale
		if keys[pygame.K_DOWN]:
			player_y += player_speed * frame_scale

		player_x = max(player_width, min(player_x, 800 - player_width))
		player_y = max(0, min(player_y, 600 - player_height))

		for bullet in bullets:
			bullet[1] -= bullet_speed
		bullets = [bullet for bullet in bullets if bullet[1] > 0]

		# 弾がSTART、EXIT、CUSTOMのどれかに当たったかを確認する
		remaining_bullets = []
		for bullet in bullets:
			bullet_rect = pygame.Rect(int(bullet[0] - 2), int(bullet[1] - 10), 4, 10)
			if start_button.colliderect(bullet_rect):
				# STARTに当たった弾を消してからステージ選択画面を開く
				bullets.clear()
				audio_manager.play_menu_select()
				for enemy in enemies:
					enemy["speed"] = enemy_speed
				stage_result = show_stage_menu()
				if stage_result is False:
					return False
				if stage_result is None:
					continue
				selected_stage = stage_result
				stage_config = stages.STAGE_CONFIGS[selected_stage]
				boss_defeat_count = stage_config["boss_defeat_count"]
				boss_shot_interval = stage_config.get("boss_spread_shot_interval", 1000)
				enemy_count = stage_config["enemy_count"]
				enemy_types = stage_config.get("enemy_types", settings.ENEMY_TYPES)
				enemies = entities.create_initial_enemies(
					enemy_count, enemy_size, enemy_speed, enemy_types
				)
				return True
			if exit_button.colliderect(bullet_rect):
				# EXITに当たった弾を消してからプログラムを終了する
				bullets.clear()
				audio_manager.play_menu_select()
				return False
			if custom_button.colliderect(bullet_rect):
				# CUSTOMに当たった弾を消してから設定画面を開く
				bullets.clear()
				audio_manager.play_menu_select()
				# CUSTOM画面から戻った後もメニューを続ける
				custom_result = show_custom_menu()
				if custom_result is False:
					return False
				continue
			if score_button.colliderect(bullet_rect):
				bullets.clear()
				audio_manager.play_menu_select()
				if not show_scores_menu():
					return False
				continue
			remaining_bullets.append(bullet)
		bullets = remaining_bullets

		ui.draw_menu(screen, sys.modules[__name__])

	return True


def show_scores_menu():
	global player_x, player_y, bullets
	# SCOREを開いた直後はステージ1を表示し、上部ボタンで表示を切り替える
	selected_stage = 1
	while True:
		frame_scale = clock.tick(60) / (1000 / 60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				bullets.append([player_x, player_y])

		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT]:
			player_x -= player_speed * frame_scale
		if keys[pygame.K_RIGHT]:
			player_x += player_speed * frame_scale
		if keys[pygame.K_UP]:
			player_y -= player_speed * frame_scale
		if keys[pygame.K_DOWN]:
			player_y += player_speed * frame_scale
		player_x = max(player_width, min(player_x, settings.SCREEN_WIDTH - player_width))
		player_y = max(0, min(player_y, settings.SCREEN_HEIGHT - player_height))

		for bullet in bullets:
			bullet[1] -= bullet_speed
		bullets = [bullet for bullet in bullets if bullet[1] > 0]
		for bullet in bullets:
			bullet_rect = pygame.Rect(int(bullet[0] - 2), int(bullet[1] - 10), 4, 10)
			if score_table_back_button.colliderect(bullet_rect):
				bullets.clear()
				return True
			for stage_number, button in enumerate(score_table_stage_buttons, start=1):
				if button.colliderect(bullet_rect):
					selected_stage = stage_number
					bullets.clear()
					break

		ui.draw_scores_menu(
			screen,
			sys.modules[__name__],
			high_scores,
			selected_stage,
			score_table_stage_buttons,
			score_table_back_button,
		)


def enter_score_name(stage, final_score):
	global high_scores
	# ステージ別トップ10に入らないスコアなら、名前入力を省略する
	if not score_storage.qualifies(high_scores, stage, final_score):
		return True

	name = ""
	# TEXTINPUTで入力し、最大4文字までに制限する
	pygame.key.start_text_input()
	try:
		while True:
			clock.tick(60)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return False
				if event.type == pygame.TEXTINPUT:
					name = (name + event.text)[:4]
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_BACKSPACE:
						name = name[:-1]
					elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and name:
						# 空欄での登録は認めず、確定時にランキングとJSONを更新する
						score_storage.add_score(high_scores, stage, name, final_score)
						return True
			ui.draw_score_name_entry(screen, sys.modules[__name__], stage, final_score, name)
	finally:
		pygame.key.stop_text_input()


def show_stage_menu():
	global player_x, player_y, bullets

	while True:
		frame_scale = clock.tick(60) / (1000 / 60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				bullets.append([player_x, player_y])

		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT]:
			player_x -= player_speed * frame_scale
		if keys[pygame.K_RIGHT]:
			player_x += player_speed * frame_scale
		if keys[pygame.K_UP]:
			player_y -= player_speed * frame_scale
		if keys[pygame.K_DOWN]:
			player_y += player_speed * frame_scale
		player_x = max(player_width, min(player_x, settings.SCREEN_WIDTH - player_width))
		player_y = max(0, min(player_y, settings.SCREEN_HEIGHT - player_height))

		for bullet in bullets:
			bullet[1] -= bullet_speed
		bullets = [bullet for bullet in bullets if bullet[1] > 0]
		for bullet in bullets:
			bullet_rect = pygame.Rect(int(bullet[0] - 2), int(bullet[1] - 10), 4, 10)
			for stage_number, button in enumerate(stage_buttons, start=1):
				if button.colliderect(bullet_rect):
					bullets.clear()
					return stage_number
			if stage_back_button.colliderect(bullet_rect):
				bullets.clear()
				return None

		ui.draw_stage_menu(screen, sys.modules[__name__], stage_buttons, stage_back_button)


# ==================================================
# 設定画面（CUSTOM）の処理
# 弾を各ボタンに当てて速度や色反転を変更する
# ==================================================
def show_custom_menu():
	global player_x, player_y, bullets
	global player_speed, bullet_speed, enemy_speed, color_inverted

	# 設定画面を表示する
	custom_running = True
	while custom_running:
		frame_scale = clock.tick(60) / (1000 / 60)
		# ---------- 設定画面の入力処理 ----------
		# CUSTOM画面でのキー入力を処理する
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					# スペースキーでプレイヤーの位置から弾を発射する
					bullets.append([player_x, player_y])
		# 設定画面でも矢印キーでプレイヤーを移動させる
		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT]:
			player_x -= player_speed * frame_scale
		if keys[pygame.K_RIGHT]:
			player_x += player_speed * frame_scale
		if keys[pygame.K_UP]:
			player_y -= player_speed * frame_scale
		if keys[pygame.K_DOWN]:
			player_y += player_speed * frame_scale
		player_x = max(player_width, min(player_x, 800 - player_width))
		player_y = max(0, min(player_y, 600 - player_height))

		# 設定画面でも弾を上へ移動させる
		for bullet in bullets:
			bullet[1] -= bullet_speed
		bullets = [bullet for bullet in bullets if bullet[1] > 0]

		# ---------- 設定値の変更処理 ----------
		# 速度設定の左右に、弾を当てるための矢印を配置する
		arrow_y_positions = [130, 220, 310]
		left_arrows = [pygame.Rect(80, y - 20, 70, 40) for y in arrow_y_positions]
		right_arrows = [pygame.Rect(650, y - 20, 70, 40) for y in arrow_y_positions]
		color_toggle_button = pygame.Rect(250, 370, 300, 40)
		reset_button = pygame.Rect(100, 420, 250, 50)
		back_button = pygame.Rect(450, 420, 250, 50)
		remaining_bullets = []
		for bullet in bullets:
			bullet_rect = pygame.Rect(int(bullet[0] - 2), int(bullet[1] - 10), 4, 10)
			hit_arrow = False
			for index, arrow in enumerate(left_arrows):
				if arrow.colliderect(bullet_rect):
					if index == 0:
						enemy_speed = max(enemy_speed_min, enemy_speed - enemy_speed_step)
					elif index == 1:
						bullet_speed = max(bullet_speed_min, bullet_speed - bullet_speed_step)
					else:
						player_speed = max(player_speed_min, player_speed - player_speed_step)
					audio_manager.play_menu_select()
					hit_arrow = True
					break
			for index, arrow in enumerate(right_arrows):
				if arrow.colliderect(bullet_rect):
					if index == 0:
						enemy_speed = min(enemy_speed_max, enemy_speed + enemy_speed_step)
					elif index == 1:
						bullet_speed = min(bullet_speed_max, bullet_speed + bullet_speed_step)
					else:
						player_speed = min(player_speed_max, player_speed + player_speed_step)
					audio_manager.play_menu_select()
					hit_arrow = True
					break
			if reset_button.colliderect(bullet_rect):
				# 初期設定ボタンに弾が当たったら速度を初期化する
				player_speed = default_player_speed
				bullet_speed = default_bullet_speed
				enemy_speed = default_enemy_speed
				color_inverted = False
				audio_manager.play_menu_select()
				hit_arrow = True
			if back_button.colliderect(bullet_rect):
				# タイトルへ戻るボタンに弾が当たったらメニューへ戻る
				audio_manager.play_menu_select()
				return "title"
			if color_toggle_button.colliderect(bullet_rect):
				# 色反転ボタンに弾が当たったら表示色を切り替える
				color_inverted = not color_inverted
				audio_manager.play_menu_select()
				hit_arrow = True
			if not hit_arrow:
				remaining_bullets.append(bullet)
		bullets = remaining_bullets

		ui.draw_custom_menu(
			screen,
			sys.modules[__name__],
			arrow_y_positions,
			left_arrows,
			right_arrows,
			color_toggle_button,
			reset_button,
			back_button,
		)

	return True


def reset_game_state():
	"""タイトルへ戻るときやゲームオーバー後に、現在のゲーム状態を初期化する。"""
	global player_x, player_y, player_alive, player_hp, player_dead_time
	global score, player_invincible_until, player_shielded, spread_shot_level
	global enemies_defeated, enemy_count, boss_defeat_count, boss_shot_interval
	global boss, boss_hp, boss_respawn_at, respawn_progress, next_respawn_count
	global charge_start_time, enemies

	# プレイヤー、スコア、強化状態を初期値へ戻す
	player_x = settings.PLAYER_START_X
	player_y = settings.PLAYER_START_Y
	player_alive = True
	player_hp = settings.PLAYER_MAX_HP
	player_dead_time = None
	score = 0
	player_invincible_until = 0
	player_shielded = False
	spread_shot_level = 0
	enemies_defeated = 0
	# 選択中ステージの進行設定を戻し、ボス戦も解除する
	enemy_count = stage_config["enemy_count"]
	boss_defeat_count = stage_config["boss_defeat_count"]
	boss_shot_interval = stage_config.get("boss_spread_shot_interval", 1000)
	boss = None
	boss_hp = settings.BOSS_INITIAL_HP
	boss_respawn_at = None
	respawn_progress = 0
	next_respawn_count = respawn_interval
	charge_start_time = None
	# 前のゲームに属する弾やアイテムを消して敵を配置し直す
	boss_bullets.clear()
	boss_bounce_bullets.clear()
	bullets.clear()
	items.clear()
	enemies = entities.create_initial_enemies(enemy_count, enemy_size, enemy_speed, enemy_types)


def show_pause_menu():
	"""ゲーム更新を止めたまま、ポーズメニューの選択結果を返す。"""
	selected_index = 0
	while True:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			if event.type == pygame.KEYDOWN:
				# 上下キーで選択を循環し、Enterで再開かタイトル復帰を決める
				if event.key == pygame.K_UP:
					selected_index = (selected_index - 1) % 2
				elif event.key == pygame.K_DOWN:
					selected_index = (selected_index + 1) % 2
				elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
					return "resume" if selected_index == 0 else "title"

		ui.draw_pause_menu(screen, sys.modules[__name__], selected_index)


# ==================================================
# ゲーム本編の処理
# プレイヤーを操作し、敵を倒してスコアを増やす
# ==================================================
running = show_menu()

while running:
	frame_scale = clock.tick(60) / (1000 / 60)
	# ---------- ゲーム中の入力処理 ----------
	# キーボードや画面を閉じる操作などのイベントを確認する
	pause_result = None
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and player_alive:
			# ポーズ中にチャージが進まないよう、未発射チャージを解除する
			charge_start_time = None
			pause_result = show_pause_menu()
			break
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and player_alive:
			# スペースキーを押している間はチャージを開始する
			if charge_start_time is None:
				charge_start_time = pygame.time.get_ticks()
		elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and player_alive:
			# キーを離した時間で通常弾かチャージ弾かを決める
			if charge_start_time is not None:
				charge_time = pygame.time.get_ticks() - charge_start_time
				is_charged = charge_time >= charge_time_required
				entities.fire_bullets(
					bullets, player_x, player_y, is_charged, spread_shot_level, bullet_speed
				)
				audio_manager.play_shot()
				charge_start_time = None
		elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and not player_alive:
			# プレイヤーが倒れているときはチャージ状態を必ず解除して、再発射させない
			charge_start_time = None
	if pause_result is False:
		running = False
		break
	# 再開を選んだフレームは更新を飛ばし、次のフレームからゲームを進める
	if pause_result == "resume":
		continue
	if pause_result == "title":
		# タイトルへ戻る場合は状態を初期化してからメニューを開く
		reset_game_state()
		if not show_menu():
			running = False
			break
		continue
	if not running:
		break

	# 押されている矢印キーに応じてプレイヤーを移動させる
	keys = pygame.key.get_pressed()
	if keys[pygame.K_LEFT]:
		player_x -= player_speed * frame_scale
	if keys[pygame.K_RIGHT]:
		player_x += player_speed * frame_scale
	if keys[pygame.K_UP]:
		player_y -= player_speed * frame_scale
	if keys[pygame.K_DOWN]:
		player_y += player_speed * frame_scale

	# プレイヤーが画面の外へ出ないように位置を制限する
	player_x = max(player_width, min(player_x, 800 - player_width))
	player_y = max(0, min(player_y, 600 - player_height))

	# ---------- 敵と弾の更新処理 ----------
	game_logic.move_enemies(enemies, player_x, player_y, settings.SCREEN_WIDTH)

	# ボスは画面上部を左右に往復し、設定が有効なステージでは3方向へ弾を撃つ
	current_time = pygame.time.get_ticks()
	if boss is not None:
		# ボスの横移動速度はここで調整（現在は敵速度の2倍、最低2.0）
		boss["x"] += boss["direction"] * max(2.0, enemy_speed * 2) * frame_scale
		if boss["x"] <= boss["size"] / 2 or boss["x"] >= 800 - boss["size"] / 2:
			boss["x"] = max(boss["size"] / 2, min(boss["x"], 800 - boss["size"] / 2))
			boss["direction"] *= -1
		if (
			stage_config.get("boss_uses_spread_attack", True)
			and current_time - boss["last_shot"] >= boss_shot_interval
		):
			boss_bullet_speed = bullet_speed / 2
			boss_bullet_origin_y = boss["y"] + boss["size"]
			target_angle = math.atan2(
				player_x - boss["x"],
				player_y + player_height / 2 - boss_bullet_origin_y,
			)
			shot_angles = (
				(-25, -12.5, 0, 12.5, 25)
				if boss["hp"] <= boss["max_hp"] / 2
				else (-25, 0, 25)
			)
			for angle_degrees in shot_angles:
				angle = target_angle + math.radians(angle_degrees)
				boss_bullets.append(
					[
						boss["x"],
						boss_bullet_origin_y,
						math.sin(angle) * boss_bullet_speed,
						math.cos(angle) * boss_bullet_speed,
					]
				)
			boss["last_shot"] = current_time
		bounce_shot_interval = stage_config.get("boss_bounce_shot_interval")
		if (
			bounce_shot_interval is not None
			and current_time - boss["last_bounce_shot"] >= bounce_shot_interval
		):
			boss_bounce_bullets.extend(
				create_boss_bounce_shots(
					boss,
					player_x,
					player_y + player_height / 2,
					bullet_speed / 4,
					current_time,
				)
			)
			boss["last_bounce_shot"] = current_time

	# 画面下へ到達した敵は消し、その分の敵を上から補充する
	escaped_enemies = sum(
		1
		for enemy in enemies
		if enemy["alive"] and enemy["counts_for_respawn"] and enemy["y"] >= 600
	)
	for enemy in enemies:
		if enemy["y"] >= 600:
			enemy["alive"] = False
	for _ in range(escaped_enemies):
		enemies.append(
			entities.create_enemy(
				random.randint(0, settings.SCREEN_WIDTH - enemy_size),
				-enemy_size,
				enemy_size,
				enemy_speed,
				random.choice(enemy_types),
				random.choice([-1, 1]),
			)
		)

	# すべての弾を画面の上方向へ移動させる
	for bullet in bullets:
		if len(bullet) > 4:
			bullet[0] += bullet[3]
			bullet[1] += bullet[4]
		else:
			bullet[1] -= bullet_speed
	for boss_bullet in boss_bullets:
		boss_bullet[0] += boss_bullet[2]
		boss_bullet[1] += boss_bullet[3]
	game_logic.move_bouncing_bullets(
		boss_bounce_bullets,
		settings.SCREEN_WIDTH,
		settings.SCREEN_HEIGHT,
		current_time,
		settings.BOSS_BOUNCE_BULLET_LIFETIME,
	)
	boss_bullets = [
		boss_bullet
		for boss_bullet in boss_bullets
		if -10 <= boss_bullet[0] <= 810 and boss_bullet[1] <= 610
	]

	# 画面の上端を越えた弾をリストから削除する
	bullets = [bullet for bullet in bullets if bullet[1] > 0 and -30 <= bullet[0] <= 830]

	# プレイヤーとの衝突判定に使う四角形を作成する
	player_rect = pygame.Rect(
		player_x - player_width,
		player_y,
		player_width * 2,
		player_height,
	)

	# アイテムを下方向へ移動させ、プレイヤーが取ったら効果を発生させる
	for item in items:
		item["y"] += item_speed
	items = [item for item in items if item["y"] < 600]
	remaining_items = []
	for item in items:
		item_rect = pygame.Rect(item["x"], item["y"], item["size"], item["size"])
		if item_rect.colliderect(player_rect):
			if item["type"] == "shield":
				# ★を取ると、次に敵へ1回当たるまでプレイヤーを守る
				player_shielded = True
				audio_manager.play_item()
			elif item["type"] == "spread":
				# ￥を取るたびに通常、3方向、5方向へ強化する
				spread_shot_level = min(2, spread_shot_level + 1)
				audio_manager.play_item()
			elif player_hp < 5:
				# ❤を取ったときだけ、HPを1回復する
				player_hp += 1
				audio_manager.play_item()
			else:
				# HPが最大なら、回復アイテムを残してもう一度取れるようにする
				remaining_items.append(item)
		else:
			remaining_items.append(item)
	items = remaining_items

	# ---------- 衝突判定とスコア処理 ----------
	# 弾と敵が衝突したかを確認し、当たっていない弾だけを残す
	remaining_bullets = []
	split_enemies = []
	for bullet in bullets:
		is_charged = len(bullet) > 2 and bullet[2]
		if is_charged:
			bullet_rect = pygame.Rect(int(bullet[0] - 15), int(bullet[1] - 15), 30, 30)
		else:
			bullet_rect = pygame.Rect(int(bullet[0] - 2), int(bullet[1] - 10), 4, 10)
		hit_enemy = False
		for enemy in enemies:
			if enemy["alive"]:
				enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["size"], enemy["size"])
				if enemy_rect.colliderect(bullet_rect):
					entities.drop_item(items, enemy["x"], enemy["y"], item_drop_chance, item_size)
					enemy["alive"] = False
					split_enemies.extend(entities.split_enemy(enemy))
					audio_manager.play_hit()
					score += 1
					enemies_defeated += 1
					if enemy["counts_for_respawn"]:
						respawn_progress += 1
					hit_enemy = True
					if not is_charged:
						break
		if not hit_enemy and boss is not None:
			# ボスの三角形を囲む四角形を作り、弾との衝突を判定する
			boss_rect = pygame.Rect(
				int(boss["x"] - boss["size"] / 2),
				int(boss["y"]),
				boss["size"],
				boss["size"],
			)
			if boss_rect.colliderect(bullet_rect):
				current_time = pygame.time.get_ticks()
				# 点滅中の短い無敵時間を設け、同じ弾で連続してHPが減るのを防ぐ
				if current_time >= boss["invincible_until"]:
					if stage_config.get("boss_uses_damage_bounce_attack", True):
						# 被弾するたび、現在のプレイヤー位置へ向けて反射弾を撃つ
						boss_bounce_bullets.extend(
							create_boss_bounce_shots(
								boss,
								player_x,
								player_y + player_height / 2,
								bullet_speed / 4,
								current_time,
								single_shot=True,
							)
						)
					boss["hp"] -= 1
					score += 1
					audio_manager.play_hit()
					boss["invincible_until"] = current_time + 120
					if boss["hp"] <= 0:
						# 撃破時は❤型の回復アイテムを落とし、敵弾を消して3秒後の再開を予約する
						items.append(
							{
								"x": int(boss["x"] - item_size / 2),
								"y": int(boss["y"] + boss["size"]),
								"size": item_size,
								"type": "heal",
							}
						)
						audio_manager.play_boss_clear()
						boss = None
						boss_bullets.clear()
						boss_bounce_bullets.clear()
						boss_respawn_at = current_time + 3000
						# 次のボス戦のHPを設定した倍率で増やす
						boss_hp *= settings.BOSS_HP_MULTIPLIER
						# 次のボスまでに必要な撃破数を増やす
						boss_defeat_count += settings.BOSS_DEFEAT_COUNT_INCREASE
						# ステージ設定に応じて、次のボスの発射間隔を短くする
						boss_shot_interval = max(
							stage_config.get("boss_spread_shot_interval_min", boss_shot_interval),
							boss_shot_interval
							- stage_config.get("boss_spread_shot_interval_decrease", 0),
						)
						# 次のボス戦後に出現する通常敵数を設定値だけ増やす
						enemy_count += settings.BOSS_DEFEAT_ENEMY_COUNT_INCREASE
				# ボスに当たった弾を通常敵への判定に使わない
				hit_enemy = True
		if is_charged or not hit_enemy:
			remaining_bullets.append(bullet)
	bullets = remaining_bullets
	enemies.extend(split_enemies)

	# 設定された数の敵を倒したら通常敵を消し、ボス戦を開始する
	if (
		enemies_defeated >= boss_defeat_count
		and boss is None
		and boss_respawn_at is None
	):
		enemies.clear()
		boss_bullets.clear()
		bullets.clear()
		boss = {
			# ボスの中心のX座標と、画面上部のY座標
			"x": 400.0,
			"y": 45,
			# ボスの幅と高さ。通常の敵より大きいサイズ
			"size": 90,
			# 移動方向。1は右向き、-1は左向き
			"direction": 1,
			# ボスの初期HP
			"hp": boss_hp,
			"max_hp": boss_hp,
			# 次にダメージを受けられる時刻。0なら出現直後から攻撃が当たる
			"invincible_until": 0,
			# 最後に弾を撃った時刻。出現後の攻撃間隔を計る
			"last_shot": pygame.time.get_ticks(),
			# 最後に反射弾を撃った時刻。ステージ設定の間隔を計る
			"last_bounce_shot": pygame.time.get_ticks(),
		}
		enemies_defeated = 0

	# ボス撃破後3秒たったら通常敵を出し、次の撃破数を数え始める
	if boss_respawn_at is not None and pygame.time.get_ticks() >= boss_respawn_at:
		boss_respawn_at = None
		next_respawn_count = respawn_progress + 1
		enemies = entities.create_initial_enemies(enemy_count, enemy_size, enemy_speed, enemy_types)

	# 撃破数に応じて通常敵を追加する（ボス戦中と再出現待ちの間は停止）
	while boss is None and boss_respawn_at is None and respawn_progress >= next_respawn_count:
		enemies.append(
			entities.create_enemy(
				random.randint(0, settings.SCREEN_WIDTH - enemy_size),
				-enemy_size,
				enemy_size,
				enemy_speed,
				random.choice(enemy_types),
				random.choice([-1, 1]),
			)
		)
		# 次の出現条件を設定する
		next_respawn_count += respawn_interval

	# 敵とプレイヤーが衝突したときのダメージ処理を行う
	split_enemies = []
	for enemy in enemies:
		if enemy["alive"]:
			enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["size"], enemy["size"])
			current_time = pygame.time.get_ticks()
			if player_alive and current_time >= player_invincible_until and enemy_rect.colliderect(player_rect):
				enemy["alive"] = False
				split_enemies.extend(entities.split_enemy(enemy))
				if player_shielded:
					# ★を持っていると、敵との接触によるダメージを1回だけ無効化する
					player_shielded = False
					audio_manager.play_damage()
				else:
					player_hp -= 1
					spread_shot_level = 0
					audio_manager.play_damage()
				enemies_defeated += 1
				score += 1
				if enemy["counts_for_respawn"]:
					respawn_progress += 1
				player_invincible_until = current_time + blink_duration
				entities.drop_item(items, enemy["x"], enemy["y"], item_drop_chance, item_size)
				if player_hp <= 0 and not player_shielded:
					player_alive = False
					player_dead_time = current_time
					audio_manager.play_game_over()
	enemies.extend(split_enemies)

	# ボスの弾がプレイヤーに当たったときのダメージ処理
	remaining_boss_bullets = []
	for boss_bullet in boss_bullets:
		boss_bullet_rect = pygame.Rect(
			int(boss_bullet[0] - 5), int(boss_bullet[1] - 5), 10, 10
		)
		if player_alive and current_time >= player_invincible_until and boss_bullet_rect.colliderect(player_rect):
			if player_shielded:
				player_shielded = False
				audio_manager.play_damage()
			else:
				player_hp -= 1
				spread_shot_level = 0
				audio_manager.play_damage()
			player_invincible_until = current_time + blink_duration
			if player_hp <= 0:
				player_alive = False
				player_dead_time = current_time
				audio_manager.play_game_over()
		else:
			remaining_boss_bullets.append(boss_bullet)
	boss_bullets = remaining_boss_bullets
	remaining_bounce_bullets = []
	for boss_bullet in boss_bounce_bullets:
		boss_bullet_rect = pygame.Rect(
			int(boss_bullet[0] - 5), int(boss_bullet[1] - 5), 10, 10
		)
		if boss_bullet_rect.colliderect(player_rect):
			if player_alive and current_time >= player_invincible_until:
				if player_shielded:
					player_shielded = False
					audio_manager.play_damage()
				else:
					player_hp -= 1
					spread_shot_level = 0
					audio_manager.play_damage()
				player_invincible_until = current_time + blink_duration
				if player_hp <= 0:
					player_alive = False
					player_dead_time = current_time
					audio_manager.play_game_over()
		else:
			remaining_bounce_bullets.append(boss_bullet)
	boss_bounce_bullets = remaining_bounce_bullets

	# ---------- ゲームオーバー後の初期化処理 ----------
	# ゲームオーバー後、設定した時間が経過したらゲームを終了する
	if not player_alive and player_dead_time is not None and pygame.time.get_ticks() - player_dead_time >= game_over_delay:
		# 初期化でスコアが消える前に、上位入賞なら名前を登録する
		if not enter_score_name(selected_stage, score):
			running = False
			break
		# 次のゲームを開始できるように、ゲームの状態を初期状態へ戻す
		reset_game_state()
		# メニューでEXITが選ばれた場合だけ、プログラムを終了する
		if not show_menu():
			running = False
			break
		# STARTが選ばれたら、初期化した状態でゲームを続ける
		running = True
		continue

	# ---------- ゲーム画面の描画処理 ----------
	# 前の画面を黒で塗りつぶし、最新の状態を描画する
	screen.fill(game_color((0, 0, 0)))

	# プレイヤーを三角形として描画するための3つの頂点を作成する
	player = [
		(player_x, player_y),
		(player_x - player_width, player_y + player_height),
		(player_x + player_width, player_y + player_height),
	]
	# 被弾中は一定時間ごとにプレイヤーを表示・非表示にして点滅させる
	current_time = pygame.time.get_ticks()
	should_blink = (
		player_invincible_until > current_time
		and (current_time // 100) % 2 == 0
	)
	if player_alive and (player_invincible_until <= current_time or should_blink):
		player_color = (255, 255, 0) if spread_shot_level > 0 else (255, 255, 255)
		pygame.draw.polygon(screen, game_color(player_color), player)

	# ★を持っている間は、プレイヤーを円で囲んで表示する
	if player_alive and player_shielded:
		pygame.draw.circle(
			screen,
			game_color((255, 215, 0)),
			(int(player_x), int(player_y + player_height / 2)),
			player_width + 10,
			3,
		)

	# アイテムを★型、❤型、￥型として描画する
	for item in items:
		center_x = item["x"] + item["size"] // 2
		center_y = item["y"] + item["size"] // 2
		if item["type"] == "shield":
			star_points = []
			for index in range(10):
				angle = -math.pi / 2 + index * math.pi / 5
				radius = item["size"] // 2 if index % 2 == 0 else item["size"] // 4
				star_points.append(
					(center_x + math.cos(angle) * radius, center_y + math.sin(angle) * radius)
				)
			pygame.draw.polygon(screen, game_color((255, 215, 0)), star_points)
		elif item["type"] == "heal":
			heart_color = game_color((255, 80, 100))
			pygame.draw.circle(screen, heart_color, (center_x - 5, center_y - 2), 7)
			pygame.draw.circle(screen, heart_color, (center_x + 5, center_y - 2), 7)
			pygame.draw.polygon(
				screen,
				heart_color,
				[(center_x - 12, center_y), (center_x + 12, center_y), (center_x, center_y + 12)],
			)
		else:
			spread_text = menu_font.render("￥", True, game_color((255, 255, 0)))
			screen.blit(spread_text, spread_text.get_rect(center=(center_x, center_y)))

	# チャージ中はプレイヤーの弾の発射部分に黄色い円を表示する
	if player_alive and charge_start_time is not None:
		charge_time = current_time - charge_start_time
		is_charge_blinking = charge_time < charge_time_required and (current_time // 100) % 2 == 0
		if charge_time >= charge_time_required or is_charge_blinking:
			pygame.draw.circle(screen, game_color((255, 255, 0)), (int(player_x), int(player_y)), 8)
	
	# 敵の種類ごとに色と形を変えて描画する
	for enemy in enemies:
		if enemy["alive"]:
			enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["size"], enemy["size"])
			if enemy["type"] == "chaser":
				pygame.draw.rect(screen, game_color((255, 0, 0)), enemy_rect)
			elif enemy["type"] == "straight":
				pygame.draw.rect(screen, game_color((255, 150, 0)), enemy_rect)
			elif enemy["type"] == "horizontal":
				pygame.draw.polygon(
					screen,
					game_color((0, 200, 255)),
					[enemy_rect.midtop, enemy_rect.midright, enemy_rect.midbottom, enemy_rect.midleft],
				)
			elif enemy["type"] == "diving":
				pygame.draw.polygon(
					screen,
					game_color((255, 80, 180)),
					[enemy_rect.midtop, enemy_rect.bottomleft, enemy_rect.bottomright],
				)
			elif enemy["type"] == "splitter":
				pygame.draw.rect(screen, game_color((80, 220, 100)), enemy_rect, border_radius=5)
			else:
				pygame.draw.circle(screen, game_color((180, 0, 255)), enemy_rect.center, enemy["size"] // 2)

	# ボスは下向きの大きな三角形で描き、被弾中は点滅させる
	if boss is not None:
		boss_is_blinking = (
			boss["invincible_until"] > current_time
			and (current_time // 60) % 2 == 0
		)
		if not boss_is_blinking:
			boss_points = [
				(boss["x"] - boss["size"] / 2, boss["y"]),
				(boss["x"] + boss["size"] / 2, boss["y"]),
				(boss["x"], boss["y"] + boss["size"]),
			]
			boss_color = (0, 255, 255) if boss["hp"] <= boss["max_hp"] / 2 else (255, 0, 0)
			pygame.draw.polygon(screen, game_color(boss_color), boss_points)
		boss_hp_text = font.render(f"BOSS HP: {boss['hp']}", True, game_color((255, 0, 0)))
		screen.blit(boss_hp_text, boss_hp_text.get_rect(topleft=(10, 46)))

	# 画面上に存在する弾を黄色い四角形として描画する
	for bullet in bullets:
		if len(bullet) > 2 and bullet[2]:
			pygame.draw.circle(screen, game_color((255, 255, 0)), (int(bullet[0]), int(bullet[1])), 15)
		else:
			pygame.draw.rect(screen, game_color((255, 255, 0)), (int(bullet[0] - 2), int(bullet[1] - 10), 4, 10))
	for boss_bullet in boss_bullets:
		pygame.draw.circle(
			screen,
			game_color((255, 80, 80)),
			(int(boss_bullet[0]), int(boss_bullet[1])),
			5,
		)
	for boss_bullet in boss_bounce_bullets:
		pygame.draw.circle(
			screen,
			game_color((255, 80, 80)),
			(int(boss_bullet[0]), int(boss_bullet[1])),
			5,
		)

	# プレイヤーの現在のHPを画面右下に表示する
	hp_text = font.render(f"HP: {player_hp}", True, game_color((255, 255, 255)))
	hp_rect = hp_text.get_rect(bottomright=(780, 580))
	screen.blit(hp_text, hp_rect)
	score_hud = font.render(f"SCORE: {score}", True, game_color((255, 255, 0)))
	screen.blit(score_hud, score_hud.get_rect(topleft=(10, 10)))
	stage_text = font.render(f"STAGE {selected_stage}", True, game_color((255, 255, 255)))
	screen.blit(stage_text, stage_text.get_rect(topright=(780, 10)))

	# プレイヤーが倒されたら、画面中央にスコアを表示する
	if not player_alive:
		score_text = font.render(f"SCORE: {score}", True, game_color((255, 255, 255)))
		score_rect = score_text.get_rect(center=(400, 300))
		screen.blit(score_text, score_rect)

	# 描画した内容を画面に反映する
	pygame.display.update()

# pygameを終了する
pygame.quit()
