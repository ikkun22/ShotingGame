# 敵のリスポーン(自動生成)まで
import math
import random
import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("2D Shooting")
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
player_alive = True
player_hp = 5
score = 0
# 敵を1体倒すたびに、上から敵を1体追加する
respawn_interval = 1
next_respawn_score = respawn_interval
player_dead_time = None
game_over_delay = 5000
player_invincible_until = 0
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
					score += 1
					hit_enemy = True
					break
		if not hit_enemy:
			remaining_bullets.append(bullet)
	bullets = remaining_bullets

	# 一定数の敵を倒したら、画面上部に新しい敵を追加する
	# scoreが次の出現条件以上になっている間、敵を追加する
	while score >= next_respawn_score:
		# 新しい敵の位置や動きを辞書にまとめて、敵のリストへ追加する
		enemies.append(
			{
				# 敵が画面の横端から出ないように、x座標をランダムに決める
				"x": random.randint(0, 800 - enemy_size),
				# 画面の上端より少し上から出現させる
				"y": -enemy_size,
				# 既存の敵と同じ大きさと移動速度を設定する
				"size": enemy_size,
				"speed": enemy_speed,
				# 追加直後は、敵が生きている状態にする
				"alive": True,
			}
		)
		# 次に敵を追加するための撃破数を更新する
		next_respawn_score += respawn_interval

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

	if not player_alive and player_dead_time is not None and pygame.time.get_ticks() - player_dead_time >= game_over_delay:
		running = False

	screen.fill((0, 0, 0))

	player = [
		(player_x, player_y),
		(player_x - player_width, player_y + player_height),
		(player_x + player_width, player_y + player_height),
	]
	current_time = pygame.time.get_ticks()
	should_blink = (
		player_invincible_until > current_time
		and (current_time // 100) % 2 == 0
	)
	if player_alive and (player_invincible_until <= current_time or should_blink):
		pygame.draw.polygon(screen, (255, 255, 255), player)
	
	for enemy in enemies:
		if enemy["alive"]:
			pygame.draw.rect(screen, (255, 0, 0), (enemy["x"], enemy["y"], enemy["size"], enemy["size"]))

	for bullet in bullets:
		pygame.draw.rect(screen, (255, 255, 0), (int(bullet[0] - 2), int(bullet[1] - 10), 4, 10))

	hp_text = font.render(f"HP: {player_hp}", True, (255, 255, 255))
	hp_rect = hp_text.get_rect(bottomright=(780, 580))
	screen.blit(hp_text, hp_rect)

	if not player_alive:
		score_text = font.render(f"SCORE: {score}", True, (255, 255, 255))
		score_rect = score_text.get_rect(center=(400, 300))
		screen.blit(score_text, score_rect)

	pygame.display.update()

pygame.quit()
