# プレイヤーの表示、動かすまで
import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("2D Shooting")

# プレイヤーの位置を設定
player_x = 400
player_y = 450

# プレイヤーの移動速度
# この数値を大きくすると速く、小さくすると遅くなる
player_speed = 0.2

# プレイヤー（三角形）のサイズ
# player_widthは中心から左右の幅、player_heightは高さを表す
player_width = 15
player_height = 30

running = True

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	# 押されているキーを確認してプレイヤーを動かす
	keys = pygame.key.get_pressed()
	if keys[pygame.K_LEFT]:
		player_x -= player_speed
	if keys[pygame.K_RIGHT]:
		player_x += player_speed
	if keys[pygame.K_UP]:
		player_y -= player_speed
	if keys[pygame.K_DOWN]:
		player_y += player_speed

	# 画面を黒色で塗りつぶす
	screen.fill((0, 0, 0))

	# プレイヤーの位置を使って白い三角形を作成
	player = [
		(player_x, player_y),
		(player_x - player_width, player_y + player_height),
		(player_x + player_width, player_y + player_height),
	]
	pygame.draw.polygon(screen, (255, 255, 255), player)

	pygame.display.update()

pygame.quit()
