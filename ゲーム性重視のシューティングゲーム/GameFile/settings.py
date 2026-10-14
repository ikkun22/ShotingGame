"""ゲーム全体で使う、変更しやすい設定値。"""

# ゲーム画面の幅と高さ（ピクセル）
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
# 目標フレームレート（現在、ゲーム本体では直接60を指定しているため未使用）
FPS = 60

# プレイヤーの開始位置（画面左上を原点としたピクセル座標）
PLAYER_START_X = 400
PLAYER_START_Y = 450
# プレイヤーの移動速度（1フレームあたりのピクセル数）
PLAYER_SPEED = 3.0
# プレイヤーの当たり判定・描画に使う幅と高さ（ピクセル）
PLAYER_WIDTH = 15
PLAYER_HEIGHT = 30
# プレイヤーの最大HP
PLAYER_MAX_HP = 5
# 被弾後、再びダメージを受けるまでの無敵時間（ミリ秒）
PLAYER_BLINK_DURATION = 1000

# 通常弾の上方向への移動速度（1フレームあたりのピクセル数）
BULLET_SPEED = 10

# 敵を倒したときにアイテムが落ちる確率（0.05は5%）
ITEM_DROP_CHANCE = 0.05
# アイテムの一辺の長さ（ピクセル）
ITEM_SIZE = 24
# アイテムの下方向への移動速度（1フレームあたりのピクセル数）
ITEM_SPEED = 1

# ゲーム開始時に画面へ配置する敵の数
ENEMY_COUNT = 5
# 通常敵の一辺の長さ（ピクセル）
ENEMY_SIZE = 30
# 通常敵の移動速度（1フレームあたりのピクセル数）
ENEMY_SPEED = 1.0
# 出現する敵の種類: 追跡型、直進型、ジグザグ型
ENEMY_TYPES = ("chaser", "straight", "zigzag")
# 敵を倒すたびに追加の敵を出す間隔（撃破数）
ENEMY_RESPAWN_INTERVAL = 1

# ボス出現時のHP
BOSS_INITIAL_HP = 10
# 次のボスのHPを決める倍率（前のボスのHPに掛ける）
BOSS_HP_MULTIPLIER = 2
# ボス撃破後、次のボス出現までに必要な撃破数の増加量
BOSS_DEFEAT_COUNT_INCREASE = 10
# ボス撃破後、次回以降の通常敵数に加える数
BOSS_DEFEAT_ENEMY_COUNT_INCREASE = 1
# ボスの反射弾が消えるまでの時間（ミリ秒）
BOSS_BOUNCE_BULLET_LIFETIME = 40000

# プレイヤーが倒されてから初期化するまでの待ち時間（ミリ秒）
GAME_OVER_DELAY = 5000
# チャージ弾を撃つためにスペースキーを押し続ける時間（ミリ秒）
CHARGE_TIME_REQUIRED = 1000

# CUSTOM画面の「初期設定に戻す」で復元する各速度
DEFAULT_PLAYER_SPEED = PLAYER_SPEED
DEFAULT_BULLET_SPEED = BULLET_SPEED
DEFAULT_ENEMY_SPEED = ENEMY_SPEED

# CUSTOM画面で変更できるプレイヤー速度（最小値、最大値、矢印1回あたりの変更量）
PLAYER_SPEED_MIN = 1.0
PLAYER_SPEED_MAX = 10.0
PLAYER_SPEED_STEP = 0.5
# CUSTOM画面で変更できる弾速（最小値、最大値、矢印1回あたりの変更量）
BULLET_SPEED_MIN = 2
BULLET_SPEED_MAX = 20
BULLET_SPEED_STEP = 2
# CUSTOM画面で変更できる敵速度（最小値、最大値、矢印1回あたりの変更量）
ENEMY_SPEED_MIN = 0.5
ENEMY_SPEED_MAX = 10.0
ENEMY_SPEED_STEP = 0.5
