# プレイヤーの当たり判定、敵の複製まで
import math
import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("2D Shooting")

player_x = 400
player_y = 450

player_speed = 0.15

player_width = 15
player_height = 30

bullets = []
bullet_speed = 1

# 敵の情報を1体ずつ辞書で持ち、まとめて管理する
# x, y は位置、size は大きさ、speed は速度、alive は生存状態
# 5体を横に並べて、少しずつ上下を変えて配置する
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
# プレイヤーが生存中かどうか
player_alive = True
# プレイヤーが消えた時刻。最初は未設定
player_dead_time = None
# 2秒後にゲームを終了
game_over_delay = 2000

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

	# 生きている敵だけを順に動かす
	# プレイヤーとの距離と方向を計算し、向かってくるように移動させる
	for enemy in enemies:
		if enemy["alive"]:
			distance_x = player_x - (enemy["x"] + enemy["size"] / 2)
			distance_y = player_y - (enemy["y"] + enemy["size"] / 2)
			distance = math.hypot(distance_x, distance_y)
			if distance > 0:
				enemy["x"] += distance_x / distance * enemy["speed"]
				enemy["y"] += distance_y / distance * enemy["speed"]

	# 弾を上に進める
	for bullet in bullets:
		bullet[1] -= bullet_speed

	# 画面の上まで行った弾は消す
	bullets = [bullet for bullet in bullets if bullet[1] > 0]

	# プレイヤーの当たり判定を四角で作る
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
					hit_enemy = True
					break
		if not hit_enemy:
			remaining_bullets.append(bullet)
	bullets = remaining_bullets

	# 敵とプレイヤーが重なったら、プレイヤーを消す
	for enemy in enemies:
		if enemy["alive"]:
			enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["size"], enemy["size"])
			if player_alive and enemy_rect.colliderect(player_rect):
				player_alive = False
				player_dead_time = pygame.time.get_ticks()

	# プレイヤーが消えてから2秒後に終了する
	if not player_alive and player_dead_time is not None and pygame.time.get_ticks() - player_dead_time >= game_over_delay:
		running = False

	screen.fill((0, 0, 0))

	player = [
		(player_x, player_y),
		(player_x - player_width, player_y + player_height),
		(player_x + player_width, player_y + player_height),
	]
	# 生存中のプレイヤーだけ描画
	if player_alive:
		pygame.draw.polygon(screen, (255, 255, 255), player)
	
	# 生きている敵だけを描画する
	for enemy in enemies:
		if enemy["alive"]:
			pygame.draw.rect(screen, (255, 0, 0), (enemy["x"], enemy["y"], enemy["size"], enemy["size"]))

	# 残っている弾だけを描画する
	for bullet in bullets:
		pygame.draw.rect(screen, (255, 255, 0), (int(bullet[0] - 2), int(bullet[1] - 10), 4, 10))

	pygame.display.update()

pygame.quit()
