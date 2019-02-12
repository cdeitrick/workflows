a = """
AU1581
AU1836
AU4381
AU4993
AU5341
AU7263
AU7577
AU7574
AU7575
AU7576
AU8821
AU9400
AU10040
AU11002
AU11001
AU11091
AU11478
AU13363
AU13364
AU15487
AU15488
AU3741
AU3740
AU29957
"""

if __name__ == "__main__":
	from pathlib import Path

	sequence_folder = Path.home() / "projects" / "lipuma" / "sequences"
	output_filename = Path(__file__).parent / "samples.tsv"
	whitelist = [i for i in a.split('\n') if i]
	_sequence_folder = Path("/home/cld100/projects/lipuma")
	sequences = Path(__file__).with_name("samples.txt")
	candidates = list(_sequence_folder / i for i in sequences.read_text().split('\n'))

	filenames = dict()
	for candidate in candidates:
		name = candidate.stem
		name = name.partition('_')[0]
		if name in whitelist:
			if name in filenames:
				filenames[name].append(candidate)
			else:
				filenames[name] = [candidate]

	t = list()
	for sample_name, reads in filenames.items():
		forward = [i for i in reads if '_R1_' in str(i)][0]
		reverse = [i for i in reads if '_R2_' in str(i)][0]

		row = {
			'sampleName':  sample_name,
			'forwardRead': forward,
			'reverseRead': reverse
		}
		t.append(row)
	import pandas

	df = pandas.DataFrame(t)
	print(output_filename)
	df.to_csv(str(output_filename), sep = "\t", index = False)
