# HP・スコア
import math
import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("2D Shooting")
# HP表示に使うフォントを作成する
font = pygame.font.Font(None, 32)

player_x = 400
player_y = 450

player_speed = 0.15

player_width = 15
player_height = 30

bullets = []
bullet_speed = 1

enemy_count = 5
enemy_size = 30
enemy_speed = 0.05
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
# プレイヤーが生存しているかどうかを管理する
player_alive = True
# プレイヤーの最大HPを設定する
player_hp = 2
# プレイヤーが弾で倒した敵の数を記録する
score = 0
# プレイヤーが消えた時刻を保存する
player_dead_time = None
# HPが0になってからゲームを終了するまでの時間を設定する
game_over_delay = 5000
# 次にダメージを受けられる時刻を保存する
player_invincible_until = 0
# 被弾後に点滅して無敵になる時間を設定する
blink_duration = 1000

running = True

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
			bullets.append([player_x, player_y])

	keys = pygame.key.get_pressed()
	if keys[pygame.K_LEFT]:
		player_x -= player_speed
	if keys[pygame.K_RIGHT]:
		player_x += player_speed
	if keys[pygame.K_UP]:
		player_y -= player_speed
	if keys[pygame.K_DOWN]:
		player_y += player_speed

	player_x = max(player_width, min(player_x, 800 - player_width))
	player_y = max(0, min(player_y, 600 - player_height))

	for enemy in enemies:
		if enemy["alive"]:
			distance_x = player_x - (enemy["x"] + enemy["size"] / 2)
			distance_y = player_y - (enemy["y"] + enemy["size"] / 2)
			distance = math.hypot(distance_x, distance_y)
			if distance > 0:
				enemy["x"] += distance_x / distance * enemy["speed"]
				enemy["y"] += distance_y / distance * enemy["speed"]

	for bullet in bullets:
		bullet[1] -= bullet_speed

	bullets = [bullet for bullet in bullets if bullet[1] > 0]

	player_rect = pygame.Rect(
		player_x - player_width,
		player_y,
		player_width * 2,
		player_height,
	)

	remaining_bullets = []
	for bullet in bullets:
		bullet_rect = pygame.Rect(int(bullet[0] - 2), int(bullet[1] - 10), 4, 10)
		hit_enemy = False
		for enemy in enemies:
			if enemy["alive"]:
				enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["size"], enemy["size"])
				if enemy_rect.colliderect(bullet_rect):
					enemy["alive"] = False
					# 敵を1体倒したのでスコアを1増やす
					score += 1
					hit_enemy = True
					break
		if not hit_enemy:
			remaining_bullets.append(bullet)
	bullets = remaining_bullets

	for enemy in enemies:
		if enemy["alive"]:
			enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["size"], enemy["size"])
			# 現在時刻を使って、被弾後の無敵時間が終わったか確認する
			current_time = pygame.time.get_ticks()
			# 無敵時間中でなく、敵と重なった場合だけダメージを受ける
			if player_alive and current_time >= player_invincible_until and enemy_rect.colliderect(player_rect):
				# プレイヤーと衝突した敵を消す
				enemy["alive"] = False
				# 敵と衝突したのでプレイヤーのHPを1減らす
				player_hp -= 1
				# 被弾してから1秒間は、次のダメージを受けないようにする
				player_invincible_until = current_time + blink_duration
				# HPが0以下になったらプレイヤーを消してゲームオーバーにする
				if player_hp <= 0:
					player_alive = False
					player_dead_time = current_time

	if not player_alive and player_dead_time is not None and pygame.time.get_ticks() - player_dead_time >= game_over_delay:
		running = False

	screen.fill((0, 0, 0))

	player = [
		(player_x, player_y),
		(player_x - player_width, player_y + player_height),
		(player_x + player_width, player_y + player_height),
	]
	# 被弾中は一定間隔でプレイヤーの表示と非表示を切り替える
	current_time = pygame.time.get_ticks()
	should_blink = (
		player_invincible_until > current_time
		and (current_time // 100) % 2 == 0
	)
	# 生存中で、点滅の表示タイミングになったときだけプレイヤーを描画する
	if player_alive and (player_invincible_until <= current_time or should_blink):
		pygame.draw.polygon(screen, (255, 255, 255), player)
	
	for enemy in enemies:
		if enemy["alive"]:
			pygame.draw.rect(screen, (255, 0, 0), (enemy["x"], enemy["y"], enemy["size"], enemy["size"]))

	for bullet in bullets:
		pygame.draw.rect(screen, (255, 255, 0), (int(bullet[0] - 2), int(bullet[1] - 10), 4, 10))

	# 現在のプレイヤーHPを画面右下に表示する
	hp_text = font.render(f"HP: {player_hp}", True, (255, 255, 255))
	hp_rect = hp_text.get_rect(bottomright=(780, 580))
	screen.blit(hp_text, hp_rect)

	# プレイヤーが消えた後に、倒した敵の数をスコアとして表示する
	if not player_alive:
		score_text = font.render(f"SCORE: {score}", True, (255, 255, 255))
		score_rect = score_text.get_rect(center=(400, 300))
		screen.blit(score_text, score_rect)

	pygame.display.update()

pygame.quit()
