import itertools
import subprocess
from pathlib import Path

import pandas
from tqdm import tqdm


def convert_reference_name(sample_name: str) -> str:
	if sample_name == 'GCA_000014085.1_ASM1408v1_genomic':
		result = 'AU1054'
	elif sample_name == 'GCA_000203955.1_ASM20395v1_genomic':
		result = 'HI2424'
	else:
		result = sample_name
	return result


def mash(genome_a: Path, genome_b: Path):
	genome_a_name = convert_reference_name(genome_a.stem)
	genome_b_name = convert_reference_name(genome_b.stem)

	columns = ['reference', 'sample', 'distance', 'pvalues', 'matchingHashes']

	program_location = Path.home() / "applications" / "mash"
	command = [program_location, "dist", genome_b, genome_a]

	output = subprocess.check_output(command, universal_newlines = True, stderr = subprocess.PIPE).strip()
	# The results are tab delimited lists of Reference-ID, Query-ID, Mash-distance, P-value, and Matching-hashes:
	result = dict(zip(columns, output.split('\t')))
	result['reference'] = genome_a_name
	result['sample'] = genome_b_name

	return result


if __name__ == "__main__":
	sample_map = Path("/home/cld100/Documents/projects/lipuma/isolate_sample_map.tsv")
	contents = sample_map.read_text().split('\n')
	sample_map = dict([i.split('\t') for i in contents if i])

	au1054 = Path("/home/cld100/Documents/projects/lipuma/reference/AU1054/GCA_000014085.1_ASM1408v1_genomic.fna")
	hi2424 = Path("/home/cld100/Documents/projects/lipuma/reference/HI2424_Reference/GCA_000203955.1_ASM20395v1_genomic.fna")

	folder = Path("/media/cld100/FA86364B863608A1/Users/cld100/Storage/projects/lipuma/assemblies/")
	filenames = [i for i in folder.iterdir() if i.suffix == '.fna'] + [au1054, hi2424]
	pairwise_filenames = list(itertools.combinations(filenames, 2))
	results = list()
	index = 0
	for element in tqdm(pairwise_filenames):
		index += 1
		left_filename, right_filename = element
		mash_result = mash(left_filename, right_filename)
		results.append(mash_result)
	df = pandas.DataFrame(results)
	df.to_csv('pairwise_combinations.tsv', sep = '\t')
