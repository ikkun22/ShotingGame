# 数学計算、敵の出現位置のランダム決定、ゲーム画面の作成に使うモジュールを読み込む
import math
import random
import pygame

# pygameを使うための初期設定を行う
pygame.init()

# 800×600のゲーム画面を作成し、タイトルと文字のフォントを設定する
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("2D Shooting")
font = pygame.font.Font(None, 32)

# プレイヤーの初期位置と移動速度を設定する
player_x = 400
player_y = 450

player_speed = 0.15

# プレイヤーの大きさを設定する
player_width = 15
player_height = 30

# 発射した弾を保存するリストと、弾の移動速度を設定する
bullets = []
bullet_speed = 1

# 敵の数、大きさ、移動速度を設定する
enemy_count = 5
enemy_size = 30
enemy_speed = 0.05
# 敵の位置や生存状態を辞書に保存し、敵のリストを作成する
enemies = [
	{
		"x": 100 + i * 130,
		"y": 50 + (i % 2) * 80,
		"size": enemy_size,
		"speed": enemy_speed,
		"alive": True,
	}
	for i in range(enemy_count)
]
# プレイヤーの生存状態、HP、撃破数を管理する
player_alive = True
player_hp = 5
score = 0
# 敵を倒した数に応じて、上から敵を1体追加する
respawn_interval = 1
next_respawn_score = respawn_interval
# ゲームオーバーの判定、プレイヤーが倒されてからゲーム終了までの時間を設定する
player_dead_time = None
game_over_delay = 5000
# 被弾後の無敵時間に使う値を設定する
player_invincible_until = 0
blink_duration = 1000

# runningがTrueの間、ゲームを繰り返し更新する
running = True

while running:
	# キーボードや画面を閉じる操作などのイベントを確認する
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
			bullets.append([player_x, player_y])

	# 押されている矢印キーに応じてプレイヤーを移動させる
	keys = pygame.key.get_pressed()
	if keys[pygame.K_LEFT]:
		player_x -= player_speed
	if keys[pygame.K_RIGHT]:
		player_x += player_speed
	if keys[pygame.K_UP]:
		player_y -= player_speed
	if keys[pygame.K_DOWN]:
		player_y += player_speed

	# プレイヤーが画面の外へ出ないように位置を制限する
	player_x = max(player_width, min(player_x, 800 - player_width))
	player_y = max(0, min(player_y, 600 - player_height))

	# 生きている敵をプレイヤーの方向へ移動させる
	for enemy in enemies:
		if enemy["alive"]:
			distance_x = player_x - (enemy["x"] + enemy["size"] / 2)
			distance_y = player_y - (enemy["y"] + enemy["size"] / 2)
			distance = math.hypot(distance_x, distance_y)
			if distance > 0:
				enemy["x"] += distance_x / distance * enemy["speed"]
				enemy["y"] += distance_y / distance * enemy["speed"]

	# すべての弾を画面の上方向へ移動させる
	for bullet in bullets:
		bullet[1] -= bullet_speed

	# 画面の上端を越えた弾をリストから削除する
	bullets = [bullet for bullet in bullets if bullet[1] > 0]

	# プレイヤーとの衝突判定に使う四角形を作成する
	player_rect = pygame.Rect(
		player_x - player_width,
		player_y,
		player_width * 2,
		player_height,
	)

	# 弾と敵が衝突したかを確認し、当たっていない弾だけを残す
	remaining_bullets = []
	for bullet in bullets:
		bullet_rect = pygame.Rect(int(bullet[0] - 2), int(bullet[1] - 10), 4, 10)
		hit_enemy = False
		for enemy in enemies:
			if enemy["alive"]:
				enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["size"], enemy["size"])
				if enemy_rect.colliderect(bullet_rect):
					enemy["alive"] = False
					score += 1
					hit_enemy = True
					break
		if not hit_enemy:
			remaining_bullets.append(bullet)
	bullets = remaining_bullets

	# 撃破数が条件に達したら、上から敵を追加する
	while score >= next_respawn_score:
		enemies.append(
			{
				"x": random.randint(0, 800 - enemy_size),
				# 画面の上端より少し上から出現させる
				"y": -enemy_size,
				"size": enemy_size,
				"speed": enemy_speed,
				"alive": True,
			}
		)
		# 次の出現条件を設定する
		next_respawn_score += respawn_interval

	# 敵とプレイヤーが衝突したときのダメージ処理を行う
	for enemy in enemies:
		if enemy["alive"]:
			enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["size"], enemy["size"])
			current_time = pygame.time.get_ticks()
			if player_alive and current_time >= player_invincible_until and enemy_rect.colliderect(player_rect):
				enemy["alive"] = False
				player_hp -= 1
				# 被弾してもスコアを追加する
				score += 1
				player_invincible_until = current_time + blink_duration
				if player_hp <= 0:
					player_alive = False
					player_dead_time = current_time

	# ゲームオーバー後、設定した時間が経過したらゲームを終了する
	if not player_alive and player_dead_time is not None and pygame.time.get_ticks() - player_dead_time >= game_over_delay:
		running = False

	# 前の画面を黒で塗りつぶし、最新の状態を描画する
	screen.fill((0, 0, 0))

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
		pygame.draw.polygon(screen, (255, 255, 255), player)
	
	# 生きている敵を赤い四角形として描画する
	for enemy in enemies:
		if enemy["alive"]:
			pygame.draw.rect(screen, (255, 0, 0), (enemy["x"], enemy["y"], enemy["size"], enemy["size"]))

	# 画面上に存在する弾を黄色い四角形として描画する
	for bullet in bullets:
		pygame.draw.rect(screen, (255, 255, 0), (int(bullet[0] - 2), int(bullet[1] - 10), 4, 10))

	# プレイヤーの現在のHPを画面右下に表示する
	hp_text = font.render(f"HP: {player_hp}", True, (255, 255, 255))
	hp_rect = hp_text.get_rect(bottomright=(780, 580))
	screen.blit(hp_text, hp_rect)

	# プレイヤーが倒されたら、画面中央にスコアを表示する
	if not player_alive:
		score_text = font.render(f"SCORE: {score}", True, (255, 255, 255))
		score_rect = score_text.get_rect(center=(400, 300))
		screen.blit(score_text, score_rect)

	# 描画した内容を画面に反映する
	pygame.display.update()

# pygameを終了する
pygame.quit()
