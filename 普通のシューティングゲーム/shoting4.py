# 敵の追加、移動、当たり判定まで
import math
import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("2D Shooting")

player_x = 400
player_y = 450

player_speed = 0.2

player_width = 15
player_height = 30

bullets = []
bullet_speed = 1

# 敵の左上の座標
enemy_x = 400
enemy_y = 50
# 敵の大きさ
enemy_size = 40
# 敵の移動速度
enemy_speed = 0.05
# 敵が生存中かどうか
enemy_alive = True

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

	# 敵をプレイヤーの方向へ移動
	if enemy_alive:
		# 横方向と縦方向の距離
		distance_x = player_x - (enemy_x + enemy_size / 2)
		distance_y = player_y - (enemy_y + enemy_size / 2)
		# 敵とプレイヤーの直線距離
		distance = math.sqrt(distance_x ** 2 + distance_y ** 2)
		# 近づきすぎていなければ移動
		if distance > enemy_speed:
			# 方向をそろえて斜めにも移動
			enemy_x += distance_x / distance * enemy_speed
			enemy_y += distance_y / distance * enemy_speed

	for bullet in bullets:
		bullet[1] -= bullet_speed

	bullets = [bullet for bullet in bullets if bullet[1] > 0]

	# 敵が生存中なら弾との当たり判定を行う
	if enemy_alive:
		# 敵の当たり判定を作る
		enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_size, enemy_size)
		remaining_bullets = []
		for bullet in bullets:
			# 弾の当たり判定を作る
			bullet_rect = pygame.Rect(int(bullet[0] - 2), int(bullet[1] - 10), 4, 10)
			# 弾と敵が重なったか確認
			if enemy_rect.colliderect(bullet_rect):
				# 敵と弾を消す
				enemy_alive = False
			else:
				# 外れた弾だけ残す
				remaining_bullets.append(bullet)
		bullets = remaining_bullets

	screen.fill((0, 0, 0))

	player = [
		(player_x, player_y),
		(player_x - player_width, player_y + player_height),
		(player_x + player_width, player_y + player_height),
	]
	pygame.draw.polygon(screen, (255, 255, 255), player)
	# 生存中の敵だけ赤く描画
	if enemy_alive:
		pygame.draw.rect(screen, (255, 0, 0), (enemy_x, enemy_y, enemy_size, enemy_size))

	for bullet in bullets:
		pygame.draw.rect(screen, (255, 255, 0), (int(bullet[0] - 2), int(bullet[1] - 10), 4, 10))

	pygame.display.update()

pygame.quit()
