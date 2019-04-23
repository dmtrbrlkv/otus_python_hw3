from os.path import dirname, join
import sys

print(f"import test unit: {__file__}, {sys.argv}")
sys.path.append(join(dirname(dirname(dirname(__file__)))), "scoring")