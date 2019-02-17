import csv
from pathlib import Path
from typing import List, Optional, Tuple, Union

from dataclasses import dataclass


@dataclass
class Sample:
	name: str
	forward: Path
	reverse: Path
	folder: Optional[Path] = None

	def exists(self):
		return self.forward.exists() and self.reverse.exists()
	@classmethod
	def from_folder(self, folder:Path, sample_id:Optional[str] = None)->'Sample':
		if not sample_id:
			sample_id = folder.name
		forward, reverse = get_sample_from_folder(folder, sample_id)

		return Sample(name = sample_id, forward = forward, reverse = reverse)

def get_sample_from_folder(folder: Path, sample_id: Optional[str] = None) -> Tuple[Path, Path]:
	candidates = [i for i in folder.glob("**/*") if i.suffix in {'.gz', '.fastq'}]
	candidates = [i for i in candidates if i.name.startswith(sample_id)]

	forward = [i for i in candidates if 'R1' in i.stem]
	reverse = [i for i in candidates if 'R2' in i.stem]

	return forward[0], reverse[0]


def read_sample_list(path: Path) -> List[Sample]:
	""" Reads a tsv file with three columns: `forward`, `reverse` and `name`"""
	samples = list()
	with path.open() as csv_file:
		reader = csv.DictReader(csv_file, delimiter = '\t')

		for row in reader:
			sample = Sample(
				row['sampleName'], row['forwardRead'], row['reverseRead'], None
			)
			samples.append(sample)
	return samples


def checkdir(path: Union[str, Path]) -> Path:
	path = Path(path)
	if not path.exists():
		path.mkdir()
	return path
