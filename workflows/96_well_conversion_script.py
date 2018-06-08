from pathlib import Path
import itertools
from pprint import pprint
if __name__ == "__main__":
	filename = Path.home() / "Downloads" / "eks_rpfR_test_GC.txt"

	contents = filename.read_text()

	contents = [[j for j in i.split("\t") if j] for i in contents.split("\n")]

	contents = contents[3:]
	group_elements = dict()

	for index, line in enumerate(contents):
		if not line:continue
		if ':' in line[0]:

			data = {
				'time': line[0],
				'temp': line[1],
				'elements': list(itertools.takewhile(lambda s: len(s) > 3, contents[index:]))
			}
			group_elements[line[0]] = data
		else:
			pass
	table = list()
	for t, block in group_elements.items():
		block_time = block['time']
		block_temp = float(block['temp'])
		block_elements = block['elements']

		for row_label, row in zip("ABCDEFGH", block_elements):
			if ':' in row[0]: row = row[2:]

			for column_label, value in zip(range(1,13), row):
				data_point = {
					'time': block_time,
					'temperature': block_temp,
					'columnLabel': column_label,
					'rowLabel': row_label,
					'value': float(value)
				}
				table.append(data_point)

	#pprint(table)
	import pandas
	pandas.DataFrame(table).to_csv(filename.with_suffix('.tsv'), sep = "\t", index = False)
