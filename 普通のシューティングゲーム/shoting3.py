# プレイヤーの弾発射、移動制限まで
import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("2D Shooting")

player_x = 400
player_y = 450

player_speed = 0.2

player_width = 15
player_height = 30

# 発射した弾を保存するリスト
bullets = []
# 弾の速度
bullet_speed = 1

running = True

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
			# プレイヤーの先端から弾を発射
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

	# プレイヤー全体が画面内に収まるように移動範囲を制限
	player_x = max(player_width, min(player_x, 800 - player_width))
	player_y = max(0, min(player_y, 600 - player_height))

	# 弾を上方向へ移動
	for bullet in bullets:
		bullet[1] -= bullet_speed

	# 画面外に出た弾を削除
	bullets = [bullet for bullet in bullets if bullet[1] > 0]

	screen.fill((0, 0, 0))

	player = [
		(player_x, player_y),
		(player_x - player_width, player_y + player_height),
		(player_x + player_width, player_y + player_height),
	]
	pygame.draw.polygon(screen, (255, 255, 255), player)

	# 弾を縦線として描画
	for bullet in bullets:
		pygame.draw.rect(screen, (255, 255, 0), (int(bullet[0] - 2), int(bullet[1] - 10), 4, 10))

	pygame.display.update()

pygame.quit()
