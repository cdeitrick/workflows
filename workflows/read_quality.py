from pathlib import Path
from typing import List, Union

from dataclasses import dataclass
import logging
logger = logging.getLogger(__name__)
try:
	from workflows import common
except ModuleNotFoundError:
	import common

import argparse


@dataclass
class TrimmomaticOutput:
	forward: Path
	reverse: Path
	unpaired_forward: Path
	unpaired_reverse: Path

	def exists(self):
		f = self.forward.exists()
		r = self.reverse.exists()
		fu = self.unpaired_forward.exists()
		ru = self.unpaired_reverse.exists()

		return f and r and fu and ru

ADAPTERS_FILENAME = Path(__file__).parent / "resources" / "adapters.fa"
@dataclass
class TrimmomaticOptions:
	# leading: int = 20
	# trailing: int = 20
	leading: int = 3
	trailing: int = 3
	window: str = "4:15"
	# minimum_length: int = 70
	minimum_length: int = 36
	#clip: Union[str, Path] = Path("/opt/trimmomatic/Trimmomatic-0.36/adapters/NexteraPE-PE.fa")
	clip: Path =  ADAPTERS_FILENAME
	job_name: str = "trimmomatic"
	threads: int = 8


@dataclass
class FastQCOutput:
	folder: Path
	reports: List[Path]

	def exists(self):
		return all(i.exists() for i in self.reports)


def fastqc(output_folder: Path, forward: Path, reverse: Path, unpaired_forward: Path = None, unpaired_reverse: Path = None) -> FastQCOutput:
	reads = [forward, reverse]
	if unpaired_forward:
		reads.append(unpaired_forward)
	if unpaired_reverse:
		reads.append(unpaired_reverse)

	fastqc_command = [
		"fastqc",
		"--outdir", output_folder
	]
	fastqc_command += reads

	output = FastQCOutput(
		output_folder,
		[output_folder / (i.name + '.html') for i in reads]
	)

	if not output.exists():
		common.run_command(common.programs.fastqc, fastqc_command, output_folder, use_srun = False)
	return output


def trimmomatic(forward: Path, reverse: Path, **kwargs) -> TrimmomaticOutput:
	"""
	Parameters
	----------
	forward, reverse:Path
		The reads to trim.
	Attributes
	----------
	output: TrimmomaticOutput
		Contains the locations of the relevant output files.
	Usage
	-----
	Trimmomatic(forward_read, reverse_read, parent_folder = parent_folder)
	output:
	parent_folder
		trimmomatic_output
			forward_trimmed_read
			reverse_trimmed_read
			forward_unparied_trimmed_read
			reverse_unpaired_trimmed_read
			trimmomatic_command.text
			trimmomatic_stderr.txt
			trimmomatic_stdout.txt
	"""
	# program_location = 'trimmomatic'

	trimmomatic_threads = kwargs.get('threads')
	prefix = kwargs.get('prefix', forward.stem)
	prefix = prefix if prefix else forward.stem
	output_folder = common.get_output_folder("trimmomatic", **kwargs)

	options = kwargs.get("options", TrimmomaticOptions())

	forward_output = output_folder / '{}.forward.trimmed.paired.fastq'.format(prefix)
	reverse_output = output_folder / '{}.reverse.trimmed.paired.fastq'.format(prefix)
	forward_output_unpaired = output_folder / '{}.forward.trimmed.unpaired.fastq'.format(prefix)
	reverse_output_unpaired = output_folder / '{}.reverse.trimmed.unpaired.fastq'.format(prefix)
	log_file = output_folder / "{}.trimmomatic_log.txt".format(prefix)
	output = TrimmomaticOutput(
		forward_output,
		reverse_output,
		forward_output_unpaired,
		reverse_output_unpaired
	)
	command = [
		common.programs.trimmomatic, "PE",
		# "-threads", str(self.options.threads),
		"-phred33",
		"-trimlog", log_file,
		# "name", self.options.job_name,
		forward,
		reverse,
		forward_output, forward_output_unpaired,
		reverse_output, reverse_output_unpaired,
		f"ILLUMINACLIP:{options.clip}:2:30:10",
		f"LEADING:{options.leading}",
		f"TRAILING:{options.trailing}",
		f"SLIDINGWINDOW:{options.window}",
		f"MINLEN:{options.minimum_length}"
	]
	if not output.exists():
		if trimmomatic_threads:
			trimmomatic_threads = None  # ('-threads', trimmomatic_threads)
		common.run_command("trimmomatic", command, output_folder,
			threads = trimmomatic_threads)
	return output


def workflow(forward: Path, reverse: Path, parent_folder:Path, options: TrimmomaticOptions, prefix = None, run_fastqc:bool = True) -> TrimmomaticOutput:
	trimmomatic_folder = common.checkdir(parent_folder / "trimmomatic")
	if run_fastqc:
		fastqc_folder = common.checkdir(parent_folder / "fastqc_untrimmed")
		fastqc_after = common.checkdir(parent_folder / "fastqc_after")
		fastqc(fastqc_folder, forward, reverse)

	trimmomatic_output = trimmomatic(forward, reverse, output_folder = trimmomatic_folder, options = options, prefix = prefix)

	if run_fastqc:
		fastqc(
			fastqc_after,
			trimmomatic_output.forward,
			trimmomatic_output.reverse,
			trimmomatic_output.unpaired_forward,
			trimmomatic_output.unpaired_reverse
		)

	return trimmomatic_output


def get_commandline_parser(subparser: common.SubparserType = None) -> argparse.ArgumentParser:
	if subparser:
		read_quality_parser = subparser.add_parser("read-quality")
	else:
		read_quality_parser = argparse.ArgumentParser(
			description = "Read pre-processing."
		)

	read_quality_parser.add_argument(
		"-n", "--name",
		action = 'store',
		help = "Name of the sample. Used when naming the output files.",
		dest = "name"
	)
	read_quality_parser.add_argument(
		"-f", "--forward",
		action = "store",
		help = "Path the the forward read.",
		dest = 'forward',
		type = Path
	)
	read_quality_parser.add_argument(
		"-r", "--reverse",
		action = "store",
		help = "Path the the reverse read",
		dest = "reverse",
		type = Path
	)
	read_quality_parser.add_argument(
		"-p", "--parent-folder",
		action = 'store',
		help = "Path to the output folder.",
		type = Path,
		dest = 'parent_folder'
	)
	return read_quality_parser


if __name__ == "__main__":
	parser = get_commandline_parser()
	args = parser.parse_args()
	default_options = TrimmomaticOptions()
	workflow(args.forward, args.reverse, args.parent_folder, options = default_options)
