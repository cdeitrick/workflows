from pathlib import Path
if __name__ == "__main__":
	path = Path("/home/cld100/projects/lipuma/samples")

	for folder in path.iterdir():
		files = list(folder.iterdir())
		sample_name = files[0].name.split('_')[0]
		folder.rename(folder.with_name(sample_name))
