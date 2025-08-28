import unittest
from e91 import *

class e91_tester(unittest.TestCase):

  def test_protocol(self):

      a_bits, b_bits, a_choices, b_choices = e91(num_pair=100)
      S, Es, k = compute_chsh(a_bits, b_bits, a_choices, b_choices)
      s = abs(S)
      print(s)
      self.assertTrue(s<2,msg=f"{S} is not less than 2")

if __name__ == '__main__':
	unittest.main()
