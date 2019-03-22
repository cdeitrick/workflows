import unittest
from pathlib import Path


class TestWorkflow(unittest.TestCase):
	def setUp(self):
		self.filename = Path(__file__) / "data" / "REL8593A.fastq"

	def test_workflow_output(self):
		pass


if __name__ == "__main__":
	pass
