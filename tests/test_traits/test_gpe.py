import alife.traits.fast_gpe as gpe
from alife.traits.fast_gpe import compute_gpe_raw
import unittest
import numpy as np

class testComputeGPE(unittest.TestCase):
    def TestAgreesWithMarkImplementation(self):
        childs = np.array([2,2,3,3,3,3])
        parents = np.array([4,2,2,2,2,4])
        childchar = childs/np.mean(childs)
        parchar = parents/np.mean(parents)
        anctraits = np.array([1,1,0,0,0,0])
        dectraits = np.array([0,1,1,1,1,0])
        t1,t2,t3,_ = compute_gpe_raw(anctraits, dectraits, childchar,parchar, False)
        self.assertEqual(
            (t1,t2,t3),
            (-0.08333333333333336, 0.25, -0.16666666666666666)
        )

if __name__ == '__main__':
    unittest.main()

