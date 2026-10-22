"""ゲームの起動入口。"""

from pathlib import Path
import runpy
import sys


if __name__ == "__main__":
	game_folder = Path(__file__).resolve().parent
	sys.path.insert(0, str(game_folder))
	game_script = game_folder / "BatteryShoting.py"
	runpy.run_path(str(game_script), run_name="__main__")