"""メニューと設定画面の描画処理。"""

import pygame


_battery_last_poll = None
_battery_percent = None


def game_color(color, inverted):
	if inverted:
		return tuple(255 - value for value in color)
	return color


def draw_battery_indicator(screen, state):
	"""バッテリー残量を画面右下に表示する。"""
	global _battery_last_poll, _battery_percent
	current_time = pygame.time.get_ticks()
	if _battery_last_poll is None or current_time - _battery_last_poll >= 1000:
		_battery_percent = state.battery_status.get_battery_percent()
		_battery_last_poll = current_time

	value = "--" if _battery_percent is None else str(_battery_percent)
	foreground = game_color((255, 255, 255), state.color_inverted)
	label = state.button_font.render(
		f"{value}%",
		True,
		foreground,
	)
	center_y = state.settings.SCREEN_HEIGHT - 24
	body = pygame.Rect(state.settings.SCREEN_WIDTH - 94, center_y - 14, 78, 28)
	terminal = pygame.Rect(body.right, center_y - 6, 5, 12)
	pygame.draw.rect(screen, foreground, body, 2, border_radius=6)
	pygame.draw.rect(screen, foreground, terminal, border_radius=2)

	interior = pygame.Rect(body.x + 5, body.y + 5, body.width - 10, body.height - 10)
	segment_gap = 2
	segment_width = (interior.width - segment_gap * 3) // 4
	percent = 0 if _battery_percent is None else max(0, min(100, _battery_percent))
	fill_color = (100, 230, 100)
	if percent <= 20:
		fill_color = (255, 75, 75)
	elif percent <= 50:
		fill_color = (255, 210, 55)
	fill_color = game_color(fill_color, state.color_inverted)
	for index in range(4):
		segment = pygame.Rect(
			interior.x + index * (segment_width + segment_gap),
			interior.y,
			segment_width,
			interior.height,
		)
		pygame.draw.rect(screen, game_color((65, 65, 65), state.color_inverted), segment)
		segment_percent = max(0, min(25, percent - index * 25))
		fill_width = round(segment.width * segment_percent / 25)
		if fill_width:
			pygame.draw.rect(
				screen,
				fill_color,
				(segment.x, segment.y, fill_width, segment.height),
			)

	label_rect = label.get_rect(midright=(body.x - 10, center_y))
	screen.blit(label, label_rect)


def draw_status_bars(screen, state):
	"""HPとスタミナを、最大値に応じた長さのゲージとして表示する。"""
	color = lambda rgb: game_color(rgb, state.color_inverted)
	hp_bar_width = max(20, state.player_max_hp * 20)
	hp_bar = pygame.Rect(10, 18, hp_bar_width, 14)
	pygame.draw.rect(screen, color((70, 70, 70)), hp_bar)
	hp_fill_width = round(hp_bar_width * state.player_hp / state.player_max_hp)
	if hp_fill_width:
		pygame.draw.rect(
			screen,
			color((255, 0, 0)),
			(10, hp_bar.y, hp_fill_width, hp_bar.height),
		)
	pygame.draw.rect(screen, color((200, 200, 200)), hp_bar, 1)
	hp_value = state.font.render(
		f"{state.player_hp}/{state.player_max_hp}",
		True,
		color((255, 255, 255)),
	)
	screen.blit(hp_value, hp_value.get_rect(midleft=(hp_bar.right + 8, hp_bar.centery)))

	stamina_bar = pygame.Rect(10, 62, 200, 14)
	pygame.draw.rect(screen, color((70, 70, 70)), stamina_bar)
	stamina_fill_width = round(stamina_bar.width * state.player_stamina / 100)
	if stamina_fill_width:
		pygame.draw.rect(
			screen,
			color((0, 200, 0)),
			(10, stamina_bar.y, stamina_fill_width, stamina_bar.height),
		)
	pygame.draw.rect(screen, color((200, 200, 200)), stamina_bar, 1)
	stamina_value = state.font.render(
		f"{state.player_stamina}% / {state.player_stamina_max}%",
		True,
		color((255, 255, 255)),
	)
	screen.blit(
		stamina_value,
		stamina_value.get_rect(midleft=(stamina_bar.right + 8, stamina_bar.centery)),
	)


def draw_resource_countup(screen, state, hp, stamina):
	"""ゲーム開始前にHPとスタミナのカウントアップを中央へ表示する。"""
	color = lambda rgb: game_color(rgb, state.color_inverted)
	screen.fill(color((0, 0, 0)))

	title = state.title_font.render("READY", True, color((255, 255, 255)))
	screen.blit(title, title.get_rect(center=(state.settings.SCREEN_WIDTH // 2, 105)))

	center_x = state.settings.SCREEN_WIDTH // 2
	for label, value, maximum, y, bar_color, value_format in (
		("HP", hp, state.player_max_hp, 235, (255, 0, 0), "{} / {}"),
		(
			"STAMINA",
			stamina,
			state.player_stamina_max,
			385,
			(0, 200, 0),
			"{}% / {}%",
		),
	):
		label_text = state.menu_font.render(label, True, color(bar_color))
		screen.blit(label_text, label_text.get_rect(center=(center_x, y)))
		value_text = state.title_font.render(
			value_format.format(value, maximum),
			True,
			color((255, 255, 255)),
		)
		screen.blit(value_text, value_text.get_rect(center=(center_x, y + 52)))

		bar_width = 360
		bar = pygame.Rect(center_x - bar_width // 2, y + 88, bar_width, 18)
		pygame.draw.rect(screen, color((70, 70, 70)), bar)
		fill_width = round(bar_width * value / maximum) if maximum else 0
		if fill_width:
			pygame.draw.rect(
				screen,
				color(bar_color),
				(bar.x, bar.y, fill_width, bar.height),
			)
		pygame.draw.rect(screen, color((200, 200, 200)), bar, 1)

	pygame.display.update()


def draw_menu(screen, state):
	color = lambda rgb: game_color(rgb, state.color_inverted)
	screen.fill(color((0, 0, 0)))
	title = state.title_font.render("BatteryShoting", True, color((255, 255, 255)))
	screen.blit(title, title.get_rect(center=(400, 120)))

	buttons = (
		(state.start_button, (0, 150, 0), "START"),
		(state.exit_button, (150, 0, 0), "EXIT"),
		(state.custom_button, (0, 100, 150), "CUSTOM"),
		(state.score_button, (130, 90, 0), "SCORE"),
	)
	for rect, button_color, label in buttons:
		pygame.draw.rect(screen, color(button_color), rect)
		text = state.menu_font.render(label, True, color((255, 255, 255)))
		screen.blit(text, text.get_rect(center=rect.center))

	player = [
		(state.player_x, state.player_y),
		(state.player_x - state.player_width, state.player_y + state.player_height),
		(state.player_x + state.player_width, state.player_y + state.player_height),
	]
	pygame.draw.polygon(screen, color((255, 255, 255)), player)
	for bullet in state.bullets:
		pygame.draw.rect(
			screen,
			color((255, 255, 0)),
			(int(bullet[0] - 2), int(bullet[1] - 10), 4, 10),
		)
	draw_battery_indicator(screen, state)
	pygame.display.update()


def draw_scores_menu(screen, state, rankings, selected_stage, stage_buttons, back_button):
	color = lambda rgb: game_color(rgb, state.color_inverted)
	screen.fill(color((0, 0, 0)))
	# 選択中ステージのランキングだけを表示し、上部のボタンを切替操作に使う
	title = state.title_font.render(f"STAGE {selected_stage} SCORES", True, color((255, 255, 255)))
	screen.blit(title, title.get_rect(center=(400, 45)))
	for stage_number, rect in enumerate(stage_buttons, start=1):
		button_color = (160, 130, 30) if stage_number == selected_stage else (0, 100, 130)
		pygame.draw.rect(screen, color(button_color), rect)
		text = state.button_font.render(f"STAGE {stage_number}", True, color((255, 255, 255)))
		screen.blit(text, text.get_rect(center=rect.center))

	table_font = pygame.font.SysFont("yugothic", 28)
	for label, x in (("RANK", 185), ("NAME", 350), ("SCORE", 590)):
		header = table_font.render(label, True, color((180, 220, 255)))
		screen.blit(header, header.get_rect(midleft=(x, 185)))
	entries = rankings.get(str(selected_stage), [])
	# 10位まで順位欄を固定表示し、未登録の順位は空欄相当の記号で埋める
	for rank in range(10):
		if rank < len(entries):
			name = entries[rank]["name"]
			score_text = str(entries[rank]["score"])
		else:
			name = "---"
			score_text = "---"
		row_y = 220 + rank * 30
		for text, x, align in (
			(f"{rank + 1:>2}", 185, "midleft"),
			(name, 350, "midleft"),
			(score_text, 590, "midleft"),
		):
			row = table_font.render(text, True, color((255, 255, 255)))
			row_rect = row.get_rect()
			setattr(row_rect, align, (x, row_y))
			screen.blit(row, row_rect)

	pygame.draw.rect(screen, color((100, 70, 70)), back_button)
	back_text = state.button_font.render("BACK", True, color((255, 255, 255)))
	screen.blit(back_text, back_text.get_rect(center=back_button.center))
	player = [
		(state.player_x, state.player_y),
		(state.player_x - state.player_width, state.player_y + state.player_height),
		(state.player_x + state.player_width, state.player_y + state.player_height),
	]
	pygame.draw.polygon(screen, color((255, 255, 255)), player)
	for bullet in state.bullets:
		pygame.draw.rect(screen, color((255, 255, 0)),
		                 (int(bullet[0] - 2), int(bullet[1] - 10), 4, 10))
	draw_battery_indicator(screen, state)
	pygame.display.update()


def draw_score_name_entry(screen, state, stage, score, name):
	color = lambda rgb: game_color(rgb, state.color_inverted)
	screen.fill(color((0, 0, 0)))
	# ゲームオーバー時の得点と入力中の名前を登録前に確認できるよう表示する
	title = state.title_font.render("NEW HIGH SCORE", True, color((255, 220, 80)))
	screen.blit(title, title.get_rect(center=(400, 180)))
	stage_text = state.menu_font.render(f"STAGE {stage}  SCORE {score}", True, color((255, 255, 255)))
	screen.blit(stage_text, stage_text.get_rect(center=(400, 260)))
	name_text = state.menu_font.render(f"NAME (4 characters): {name}_", True, color((255, 255, 255)))
	screen.blit(name_text, name_text.get_rect(center=(400, 340)))
	hint = state.button_font.render("ENTER: 登録", True, color((180, 220, 255)))
	screen.blit(hint, hint.get_rect(center=(400, 410)))
	draw_battery_indicator(screen, state)
	pygame.display.update()


def draw_stage_menu(screen, state, stage_buttons, back_button):
	color = lambda rgb: game_color(rgb, state.color_inverted)
	screen.fill(color((0, 0, 0)))
	title = state.title_font.render("STAGE SELECT", True, color((255, 255, 255)))
	screen.blit(title, title.get_rect(center=(400, 120)))

	for stage_number, rect in enumerate(stage_buttons, start=1):
		pygame.draw.rect(screen, color((0, 100 + stage_number * 20, 130)), rect)
		text = state.menu_font.render(f"STAGE {stage_number}", True, color((255, 255, 255)))
		screen.blit(text, text.get_rect(center=rect.center))

	pygame.draw.rect(screen, color((100, 70, 70)), back_button)
	back_text = state.button_font.render("BACK", True, color((255, 255, 255)))
	screen.blit(back_text, back_text.get_rect(center=back_button.center))

	player = [
		(state.player_x, state.player_y),
		(state.player_x - state.player_width, state.player_y + state.player_height),
		(state.player_x + state.player_width, state.player_y + state.player_height),
	]
	pygame.draw.polygon(screen, color((255, 255, 255)), player)
	for bullet in state.bullets:
		pygame.draw.rect(
			screen,
			color((255, 255, 0)),
			(int(bullet[0] - 2), int(bullet[1] - 10), 4, 10),
		)

	instruction = state.menu_font.render("撃ってステージを選択", True, color((200, 200, 200)))
	screen.blit(instruction, instruction.get_rect(center=(400, 200)))
	draw_battery_indicator(screen, state)
	pygame.display.update()


def draw_custom_menu(screen, state, arrow_y_positions, left_arrows, right_arrows,
                     color_toggle_button, reset_button, back_button):
	color = lambda rgb: game_color(rgb, state.color_inverted)
	screen.fill(color((0, 0, 0)))
	title = state.title_font.render("CUSTOM", True, color((255, 255, 255)))
	screen.blit(title, title.get_rect(center=(400, 55)))

	options = (
		f"敵の速度: {state.enemy_speed:.1f}",
		f"弾の速度: {state.bullet_speed:.0f}",
		f"プレイヤー速度: {state.player_speed:.1f}",
	)
	for index, option in enumerate(options):
		text = state.menu_font.render(option, True, color((255, 255, 255)))
		screen.blit(text, text.get_rect(center=(400, 130 + index * 90)))

	for arrow in left_arrows:
		pygame.draw.rect(screen, color((150, 70, 70)), arrow)
	for arrow in right_arrows:
		pygame.draw.rect(screen, color((70, 150, 70)), arrow)
	for y in arrow_y_positions:
		left_text = state.menu_font.render("←", True, color((255, 255, 255)))
		right_text = state.menu_font.render("→", True, color((255, 255, 255)))
		screen.blit(left_text, left_text.get_rect(center=(115, y)))
		screen.blit(right_text, right_text.get_rect(center=(685, y)))

	button_color = (0, 150, 0) if state.color_inverted else (150, 0, 0)
	pygame.draw.rect(screen, color(button_color), color_toggle_button)
	color_text = state.menu_font.render(
		f"色反転: {'ON' if state.color_inverted else 'OFF'}",
		True,
		color((255, 255, 255)),
	)
	screen.blit(color_text, color_text.get_rect(center=color_toggle_button.center))

	pygame.draw.rect(screen, color((120, 90, 0)), reset_button)
	pygame.draw.rect(screen, color((0, 100, 150)), back_button)
	for rect, label in ((reset_button, "初期設定に戻す"), (back_button, "タイトルへ戻る")):
		text = state.button_font.render(label, True, color((255, 255, 255)))
		screen.blit(text, text.get_rect(center=rect.center))

	player = [
		(state.player_x, state.player_y),
		(state.player_x - state.player_width, state.player_y + state.player_height),
		(state.player_x + state.player_width, state.player_y + state.player_height),
	]
	pygame.draw.polygon(screen, color((255, 255, 255)), player)
	for bullet in state.bullets:
		pygame.draw.rect(
			screen,
			color((255, 255, 0)),
			(int(bullet[0] - 2), int(bullet[1] - 10), 4, 10),
		)

	instruction = state.menu_font.render("SPACE:発射", True, color((200, 200, 200)))
	screen.blit(instruction, instruction.get_rect(center=(400, 550)))
	draw_battery_indicator(screen, state)
	pygame.display.update()


def draw_pause_menu(screen, state, selected_index):
	color = lambda rgb: game_color(rgb, state.color_inverted)
	# ゲーム画面を暗くして、ポーズ中であることを示す
	overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
	overlay.fill((0, 0, 0, 170))
	screen.blit(overlay, (0, 0))

	panel = pygame.Rect(200, 160, 400, 280)
	pygame.draw.rect(screen, color((20, 20, 20)), panel)
	pygame.draw.rect(screen, color((180, 180, 180)), panel, 2)
	title = state.title_font.render("PAUSE", True, color((255, 255, 255)))
	screen.blit(title, title.get_rect(center=(400, 225)))

	options = ("ゲームを続ける", "タイトルにもどる")
	for index, label in enumerate(options):
		option_rect = pygame.Rect(230, 285 + index * 65, 340, 50)
		# 選択中の項目だけ背景と文字色を変える
		if index == selected_index:
			pygame.draw.rect(screen, color((65, 65, 65)), option_rect)
		text_color = (255, 255, 0) if index == selected_index else (255, 255, 255)
		text = state.button_font.render(label, True, color(text_color))
		screen.blit(text, text.get_rect(center=option_rect.center))

	draw_battery_indicator(screen, state)
	pygame.display.update()
