import unittest
import math
from count_chain import CountChain


class TestLRUChain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """:arg
        this runs once at the start of test
        """
        print('setupClass')

    @classmethod
    def tearDownClass(cls):
        """:arg
                this runs once after all test is completed
        """
        print('teardownClass')

    def setUp(self):
        """:arg
                this runs before each test
        """
        self.d_list = CountChain(7)

    def tearDown(self):
        """:arg
        this runs after each test
        """
        pass

    def test_push(self):
        """:arg
        push inserts at the front of the list
        this test function tests if it does it correctly
        """
        p_list = [i for i in range(1, 8)] + [1, 1, 5, 6, 1, 2, 8, 3, 4, 7, 5, 3, 2]
        for i in p_list:
            self.d_list.push(i)
        result = {1: [5, 7, 4, 8], 2: [3], 3: [2, 1], 4: [], 5: [], 6: [], 7: [], 8: [ ]}
        self.assertEqual(self.d_list.data_display(), result)

    def test_count_reduction(self):
        p_list = [i for i in range(1, 8)] + [1, 1, 5, 6, 1, 2, 8, 3, 4, 7, 5, 3, 2] + [1, 5, 7, 2, 3, 5, 1, 3, 7, 2]
        for i in p_list:
            self.d_list.push(i)

        self.assertEqual(self.d_list.average_count, 1.57)

    def test_length(self):
        self.d_list.push(2)
        self.d_list.push(5)
        self.d_list.push(3)
        self.assertEqual(self.d_list.length, 3)
        self.d_list.push(6)
        self.assertEqual(len(self.d_list.table), 4)

    def test_boundary(self):
        for i in range(1, 7):
            self.d_list.push(i)

        self.assertEqual(self.d_list.new_boundary.data, 5)
        self.assertEqual(self.d_list.old_boundary.data, 2)

    def test_frequency_count(self):
        a = [1, 1, 2, 3, 1, 3, 2, 1, 2]
        for i in a:
            self.d_list.push(i)

        self.assertEqual(self.d_list.freq_count_display(), {i:a.count(i) for i in set(a)})


if __name__ == '__main__':
    unittest.main()
