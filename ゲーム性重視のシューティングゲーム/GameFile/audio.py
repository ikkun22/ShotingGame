"""ゲーム用の効果音を生成して再生する簡易オーディオ管理。"""

import math
from array import array

import pygame


class AudioManager:
	"""pygame.mixerで使う短い効果音を作成して再生する。"""

	def __init__(self):
		self.enabled = False
		self._sfx = {}
		self._sfx_volume = 0.55
		self._init_mixer()
		if self.enabled:
			self._sfx["shot"] = self._make_tone((330.0, 440.0), 70, 0.18)
			self._sfx["hit"] = self._make_tone((180.0, 120.0), 90, 0.20)
			self._sfx["item"] = self._make_tone((660.0, 880.0), 120, 0.18)
			self._sfx["boss_clear"] = self._make_chord((220.0, 330.0, 440.0), 200, 0.22)
			self._sfx["damage"] = self._make_tone((110.0, 90.0), 180, 0.22)
			self._sfx["game_over"] = self._make_tone((220.0, 180.0), 280, 0.24)
			self._sfx["menu_select"] = self._make_tone((520.0, 660.0), 80, 0.14)
			for sound in self._sfx.values():
				if sound is not None:
					sound.set_volume(self._sfx_volume)

	def _init_mixer(self):
		try:
			pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
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

	def play_shot(self):
		self.play("shot")

	def play_hit(self):
		self.play("hit")

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
