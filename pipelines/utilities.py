from pathlib import Path
from typing import Union
def checkdir(path:Union[str, Path])->Path:
	path = Path(path)
	if not path.exists():
		path.mkdir()
	return path