"""
	Implements classes to describe the output of various programs. These classes are placed here rather
	that the corresponding program file in order to reduce the network of dependant imports.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from loguru import logger
from pipelines import sampleio, utilities


@dataclass
class BaseSampleOutput:
	# Base class to represent the output of programs.
	# Basically, force the output files to include a set of common attributes and methods.
	name: str
	folder: Path

	def exists(self) -> bool:
		raise NotImplementedError

	@classmethod
	def expected(cls, folder, sample_name: str) -> "BaseSampleOutput":
		raise NotImplementedError

	@classmethod
	def from_folder(cls, folder: Path, sample_name: Optional[str]) -> "BaseSampleOutput":
		raise NotImplementedError


@dataclass
class BreseqOutput(BaseSampleOutput):
	index: Path
	summary: Path

	@classmethod
	def from_folder(cls, folder: Path, sample_name: Optional[str] = None) -> "BreseqOutput":
		index = folder / "output" / "index.html"
		summary = folder / "output" / "summary.html"

		if not sample_name:
			# Try to extract the sample name from the breseq output files.
			sample_name = _extract_sample_name_from_breseq_summary(summary)
			if sample_name is None:
				logger.warning(f"Could not extract the filename from {summary}")

		return BreseqOutput(sample_name, folder, index, summary)

	@classmethod
	def expected(cls, folder, sample_name: Optional[str] = None) -> "BreseqOutput":
		return cls.from_folder(folder)

	def exists(self) -> bool:
		return self.index.exists()

@dataclass
class FastQCOutput(BaseSampleOutput):
	folder: Path
	reports: List[Path]

	@classmethod
	def from_folder(cls, folder: Path, sample_name: Optional[str]) -> "FastQCOutput":
		raise NotImplementedError

	@ classmethod
	def expected(cls, folder, sample_name: str) -> "FastQCOutput":
		raise NotImplementedError

	def exists(self):
		return all(i.exists() for i in self.reports)


@dataclass
class ProkkaOutput(BaseSampleOutput):
	gff: Path
	fna: Path
	gbk: Path
	ffn: Path

	faa: Optional[Path]
	sqn: Optional[Path]
	fsa: Optional[Path]
	tbl: Optional[Path]
	err: Optional[Path]
	log: Optional[Path]
	txt: Optional[Path]
	tsv: Optional[Path]

	def exists(self):
		return self.gff.exists()

	@classmethod
	def from_folder(cls, folder: Path, sample_name: Optional[str] = None) -> "ProkkaOutput":
		if sample_name is None:
			# Assume that the fna file exists. Otherwise the output folder is incomplete and this should fail anyway.
			try:
				expected_fna = [i for i in folder.iterdir() if i.suffix == '.fna'][0]
				sample_name = expected_fna.stem
			except IndexError:
				message = f"The prokka output folder is incomplete: '{folder}'"
				raise FileNotFoundError(message)
		output = ProkkaOutput(
			name = sample_name,
			folder = folder,
			gff = utilities.get_file_by_type(folder, '.gff'),
			gbk = utilities.get_file_by_type(folder, '.gbk'),
			fna = utilities.get_file_by_type(folder, '.fna'),
			faa = utilities.get_file_by_type(folder, '.faa'),
			ffn = utilities.get_file_by_type(folder, '.ffn'),
			sqn = utilities.get_file_by_type(folder, '.sqn'),
			fsa = utilities.get_file_by_type(folder, '.fsa'),
			tbl = utilities.get_file_by_type(folder, '.tbl'),
			err = utilities.get_file_by_type(folder, '.err'),
			log = utilities.get_file_by_type(folder, '.log'),
			txt = utilities.get_file_by_type(folder, '.txt'),
			tsv = utilities.get_file_by_type(folder, '.tsv')
		)
		return output

	@classmethod
	def expected(cls, folder: Path, sample_name: str) -> "ProkkaOutput":
		basename = folder / sample_name
		output = ProkkaOutput(
			name = sample_name,
			folder = folder,
			gff = basename.with_suffix(".gff"),
			gbk = basename.with_suffix(".gbk"),
			fna = basename.with_suffix(".fna"),
			faa = basename.with_suffix(".faa"),
			ffn = basename.with_suffix(".ffn"),
			sqn = basename.with_suffix(".sqn"),
			fsa = basename.with_suffix(".fsa"),
			tbl = basename.with_suffix(".tbl"),
			err = basename.with_suffix(".err"),
			log = basename.with_suffix(".log"),
			txt = basename.with_suffix(".txt"),
			tsv = basename.with_suffix(".tsv")
		)
		return output


@dataclass
class ShovillOutput(BaseSampleOutput):
	contigs: Path
	contigs_gfa: Path
	contigs_spades: Path

	@classmethod
	def from_folder(cls, folder: Path, sample_name: Optional[str] = None) -> "ShovillOutput":
		contigs = folder / "contigs.fa"
		contigs_gfa = folder / "contigs.gfa"
		contigs_spades = folder / "spades.fasta"

		if not sample_name:
			sample_name = _get_sample_name_from_shovill_log(folder / "shovill.log")

		return ShovillOutput(sample_name, folder, contigs, contigs_gfa, contigs_spades)

	@classmethod
	def expected(cls, folder, sample_name: str) -> "ShovillOutput":
		return ShovillOutput.from_folder(folder, sample_name)

	def exists(self) -> bool:
		return self.contigs.exists()


@dataclass
class TrimmomaticOutput(BaseSampleOutput):
	name: str
	forward: Path
	reverse: Path
	unpaired_forward: Optional[Path]
	unpaired_reverse: Optional[Path]

	def reads(self) -> List[Path]:
		return [self.forward, self.reverse, self.unpaired_forward, self.unpaired_reverse]

	def exists(self) -> bool:
		f = self.forward.exists()
		r = self.reverse.exists()

		return f and r

	@classmethod
	def from_folder(cls, folder: Path, sample_name: Optional[str] = None) -> 'TrimmomaticOutput':
		forward, reverse = utilities.get_reads_from_folder(folder)
		unpaired_forward = _get_unpaired_read(folder, isforward = True)
		unpaired_reverse = _get_unpaired_read(folder, isforward = False)

		if sample_name is None:
			sample_name = forward.name.split('.')[0]

		return cls(sample_name, folder, forward, reverse, unpaired_forward, unpaired_reverse)

	@classmethod
	def expected(cls, folder: Path, sample_name: str) -> 'TrimmomaticOutput':
		forward: Path = folder / f'{sample_name}.forward.trimmed.paired.fastq'
		reverse: Path = folder / f'{sample_name}.reverse.trimmed.paired.fastq'
		unpaired_forward: Optional[Path] = folder / f'{sample_name}.forward.trimmed.unpaired.fastq'
		unpaired_reverse: Optional[Path] = folder / f'{sample_name}.reverse.trimmed.unpaired.fastq'
		return cls(sample_name, folder, forward, reverse, unpaired_forward, unpaired_reverse)

	def as_sample(self) -> sampleio.SampleReads:
		result = sampleio.SampleReads(self.name, self.forward, self.reverse)
		return result


def _extract_sample_name_from_breseq_summary(filename: Path) -> Optional[str]:
	import re
	pattern = "href=\"calibration/(?P<name>.+?)[.]error_rates.pdf\""
	contents = filename.read_text()

	match = re.search(pattern, contents)
	if match:
		fname = match.groupdict()['name']
		sample_name = fname.split('.')[0]
	else:
		sample_name = None
	return sample_name


def _get_sample_name_from_shovill_log(filename: Path) -> Optional[str]:
	contents = filename.read_text().split('\n')
	command = contents[1].split(' ')

	# Use the `--R1` and `--R2` flags to locate the read filenames.

	index_r1 = command.index('--R1')
	index_r2 = command.index('--R2')
	filename_forward = Path(command[index_r1 + 1]).stem  # Only want the filename, not the full path.
	filename_reverse = Path(command[index_r2 + 1]).stem
	sample_name = utilities.get_longest_substring(filename_forward, filename_reverse)
	if sample_name.endswith('.'): sample_name = sample_name[:-1]
	if not sample_name:
		sample_name = None
	return sample_name


def _get_unpaired_read(folder: Path, isforward: bool) -> Optional[Path]:
	files = list(i for i in folder.iterdir() if i.suffix == '.fastq')

	readtype = 'forward' if isforward else 'reverse'
	try:
		read_filename = [i for i in files if (readtype in i.name and 'unpaired' in i.name)][0]
	except IndexError:
		read_filename = None
	return read_filename
