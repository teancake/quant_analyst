import unittest

import os, sys
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
print(parent_dir)
sys.path.append(os.path.join(parent_dir,"quant_analyst"))

from data.alpha_data import Alpha101Data, Alpha191Data, MyAlphaData

class AlphaDataTest(unittest.TestCase):
    def test_my_alpha(self):
        print("testing my_alpha")
        data = MyAlphaData.get_my_alpha_data()
        print(data)
    def test_alpha101(self):
        print("testing alpha101")
        data = Alpha101Data.get_alpha101_data()
        print(data)

    def test_alpha191(self):
        print("testing alpha101")
        data = Alpha191Data.get_alpha191_data()
        print(data)


if __name__ == '__main__':
    unittest.main()