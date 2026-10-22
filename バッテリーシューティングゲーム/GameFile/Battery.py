"""Windowsのバッテリー情報を取得し、ゲーム開始時のリソースを決める。"""

import ctypes
import sys


class SystemPowerStatus(ctypes.Structure):
	_fields_ = [
		("ACLineStatus", ctypes.c_ubyte),
		("BatteryFlag", ctypes.c_ubyte),
		("BatteryLifePercent", ctypes.c_ubyte),
		("SystemStatusFlag", ctypes.c_ubyte),
		("BatteryLifeTime", ctypes.c_uint32),
		("BatteryFullLifeTime", ctypes.c_uint32),
	]


def get_system_power_status():
	"""取得できない環境ではNoneを返す。"""
	if sys.platform != "win32":
		return None

	status = SystemPowerStatus()
	kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
	get_status = kernel32.GetSystemPowerStatus
	get_status.argtypes = [ctypes.POINTER(SystemPowerStatus)]
	get_status.restype = ctypes.c_bool
	if not get_status(ctypes.byref(status)):
		return None
	return status


def get_battery_percent():
	"""現在のバッテリー残量を返す。不明な場合はNoneを返す。"""
	status = get_system_power_status()
	if status is None or status.BatteryLifePercent == 255:
		return None
	return int(status.BatteryLifePercent)


def get_game_resources(battery_percent):
	"""バッテリー残量から最大HPと最大スタミナを決める。"""
	if battery_percent is None:
		return 5, 50
	if not 0 <= battery_percent <= 100:
		raise ValueError("battery_percent must be between 0 and 100")

	# 四捨五入し、0%でもゲームを開始できるようHPは最低1にする
	max_hp = max(1, (battery_percent + 5) // 10)
	return max_hp, battery_percent


if __name__ == "__main__":
	status = get_system_power_status()
	if status is None or status.BatteryLifePercent == 255:
		print("バッテリー残量を取得できません")
	else:
		print(f"現在のバッテリー残量: {status.BatteryLifePercent}%")

	if status is not None:
		if status.ACLineStatus == 1:
			print("状態: 充電中、または電源に接続中")
		elif status.ACLineStatus == 0:
			print("状態: バッテリーで動作中")
		else:
			print("状態: 電源状態不明")
