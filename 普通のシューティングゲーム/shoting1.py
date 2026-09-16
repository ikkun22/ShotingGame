# 画面の表示まで
import pygame

# pygameを使用するための初期設定
pygame.init()

# 幅800ピクセル、高さ600ピクセルのゲーム画面を作成
screen = pygame.display.set_mode((800, 600))
# ウィンドウのタイトルを設定
pygame.display.set_caption("2D Shooting")

# ゲームを実行中かどうか
running = True

# runningがTrueの間、ゲームの処理を繰り返す
while running:
    # ウィンドウ操作やキーボード操作などのイベントを取得
    for event in pygame.event.get():
        # ウィンドウの閉じるボタンが押されたらゲームを終了
        if event.type == pygame.QUIT:
            running = False

    # 描画した内容を画面に反映
    pygame.display.update()

# pygameを終了
pygame.quit()