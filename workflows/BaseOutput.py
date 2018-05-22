from dataclasses import dataclass, asdict
from typing import Dict
from pathlib import Path
@dataclass
class BaseOutput:
	def __post_init__(self):
		data: Dict[str, Path] = asdict(self)
		is_valid = all(i.exists() for i in data.values())
		if not is_valid:
			for key, value in data.items():
				print(key, value.exists(), value)

			raise FileNotFoundError("Some output files are missing for ", self.__class__.__name__)

if __name__ == "__main__":
	pass