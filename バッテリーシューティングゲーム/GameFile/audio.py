"""ゲーム用の効果音を生成して再生する簡易オーディオ管理。"""

import math
from array import array
from pathlib import Path

import pygame


# 効果音ごとの音量（0.0～1.0）。個別に調整する場合は値を変更する。
SFX_VOLUMES = {
	"shot": 0.55,
	"charge": 0.3,
	"charged_shot": 0.25,
	"hit": 0.55,
	"player_damage": 0.55,
	"enemy_damage": 0.55,
	"dodge": 0.55,
	"item": 0.55,
	"boss_clear": 0.55,
	"damage": 0.55,
	"game_over": 0.55,
	"menu_select": 0.55,
	"menu_cancel": 0.55,
	"resource_countup": 0.55,
	"score_display": 0.4,
}

MUSIC_VOLUMES = {
	"menu_bgm": 0.3,
	"game_bgm": 0.1,
}


def _load_sound(filename):
	sound_path = Path(__file__).resolve().parent / "sounds" / filename
	return pygame.mixer.Sound(str(sound_path))


class AudioManager:
	"""pygame.mixerで使う短い効果音を作成して再生する。"""

	def __init__(self):
		self.enabled = False
		self._sfx = {}
		self._charge_channel = None
		self._music_track = None
		self._init_mixer()
		if self.enabled:
			self._sfx["shot"] = _load_sound("ショット.mp3")
			self._sfx["charge"] = _load_sound("チャージ音.mp3")
			self._sfx["charged_shot"] = _load_sound("チャージショット.mp3")
			self._sfx["hit"] = self._make_tone((180.0, 120.0), 90, 0.20)
			self._sfx["player_damage"] = _load_sound("プレイヤーダメージ.mp3")
			self._sfx["enemy_damage"] = _load_sound("敵ダメージ.mp3")
			self._sfx["dodge"] = _load_sound("回避.mp3")
			self._sfx["item"] = _load_sound("アイテム獲得音.mp3")
			self._sfx["boss_clear"] = self._make_chord((220.0, 330.0, 440.0), 200, 0.22)
			self._sfx["damage"] = self._make_tone((110.0, 90.0), 180, 0.22)
			self._sfx["game_over"] = self._make_tone((220.0, 180.0), 280, 0.24)
			self._sfx["menu_select"] = _load_sound("カーソル移動3.mp3")
			self._sfx["menu_cancel"] = _load_sound("キャンセル5.mp3")
			self._sfx["resource_countup"] = _load_sound("HP,スタミナ演出.mp3")
			self._sfx["score_display"] = _load_sound("スコア表示.mp3")
			for name, sound in self._sfx.items():
				if sound is not None:
					sound.set_volume(SFX_VOLUMES[name])

	def _init_mixer(self):
		try:
			pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
			pygame.mixer.set_num_channels(64)
			self.enabled = True
		except Exception:
			self.enabled = False

	def _make_tone(self, frequencies, duration_ms, volume):
		if not self.enabled:
			return None
		rate = 22050
		frames = int(rate * duration_ms / 1000)
		pcm = array("h")
		for index in range(frames):
			t = index / rate
			value = 0.0
			for freq in frequencies:
				value += math.sin(2.0 * math.pi * freq * t)
			value /= len(frequencies)
			envelope = 1.0 - (index / max(frames, 1)) * 0.85
			sample = int(max(-1.0, min(1.0, value * volume * envelope)) * 32767)
			pcm.append(sample)
		return pygame.mixer.Sound(buffer=pcm.tobytes())

	def _make_chord(self, frequencies, duration_ms, volume):
		if not self.enabled:
			return None
		rate = 22050
		frames = int(rate * duration_ms / 1000)
		pcm = array("h")
		for index in range(frames):
			t = index / rate
			value = 0.0
			for freq in frequencies:
				value += math.sin(2.0 * math.pi * freq * t)
			value /= len(frequencies)
			envelope = 1.0 - (index / max(frames, 1)) * 0.75
			sample = int(max(-1.0, min(1.0, value * volume * envelope)) * 32767)
			pcm.append(sample)
		return pygame.mixer.Sound(buffer=pcm.tobytes())

	def play(self, name):
		if not self.enabled:
			return
		sound = self._sfx.get(name)
		if sound is not None:
			sound.play()

	def _play_music(self, track, filename):
		if not self.enabled:
			return
		if self._music_track == track and pygame.mixer.music.get_busy():
			return
		music_path = Path(__file__).resolve().parent / "sounds" / filename
		pygame.mixer.music.load(str(music_path))
		pygame.mixer.music.set_volume(MUSIC_VOLUMES[track])
		pygame.mixer.music.play(-1)
		self._music_track = track

	def play_menu_bgm(self):
		self._play_music("menu_bgm", "ゲーム待機中BGM.mp3")

	def play_game_bgm(self):
		self._play_music("game_bgm", "ゲーム中BGM.mp3")

	def stop_menu_bgm(self):
		if self.enabled and self._music_track == "menu_bgm":
			pygame.mixer.music.stop()
			self._music_track = None

	def play_shot(self):
		self.play("shot")

	def play_charge(self):
		if not self.enabled:
			return
		self.stop_charge()
		sound = self._sfx.get("charge")
		if sound is not None:
			self._charge_channel = sound.play(loops=-1)

	def stop_charge(self):
		if self._charge_channel is not None:
			self._charge_channel.stop()
			self._charge_channel = None

	def play_charged_shot(self):
		self.play("charged_shot")

	def play_hit(self):
		self.play("hit")

	def play_player_damage(self):
		self.play("player_damage")

	def play_enemy_damage(self):
		self.play("enemy_damage")

	def play_dodge(self):
		self.play("dodge")

	def play_item(self):
		self.play("item")

	def play_boss_clear(self):
		self.play("boss_clear")

	def play_damage(self):
		self.play("damage")

	def play_game_over(self):
		self.play("game_over")

	def play_menu_select(self):
		self.play("menu_select")

	def play_menu_cancel(self):
		self.play("menu_cancel")

	def play_resource_countup(self):
		self.play("resource_countup")

	def play_score_display(self):
		self.play("score_display")
