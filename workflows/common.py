from pathlib import Path

from dataclasses import dataclass


def checkdir(path):
	if isinstance(path, str): path = Path(path)
	if not path.exists(): path.mkdir()
	return path


@dataclass
class Sample:
	name: str
	forward: Path
	reverse: Path
	folder: Path
	def exists(self):
		return self.forward.exists() and self.reverse.exists()


if __name__ == "__main__":
	pass
