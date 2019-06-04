from pathlib import Path
from pprint import pprint
if __name__ == "__main__":
	source_folder = Path("/media/cld100/FA86364B863608A1/Users/cld100/Storage/projects/lipuma/shovill_assemblies/assemblies/")

	isolate_sample_map = Path.home() / "Documents" / "projects" / "lipuma" / "isolate_sample_map.txt"

	lines = isolate_sample_map.read_text().split('\n')
	all_sample_ids = set([i.split('\t')[0] for i in lines if i])

	fasta_files = set(i.stem for i in source_folder.iterdir())

	missing = all_sample_ids - fasta_files
	print(len(missing))
	pprint(missing)



