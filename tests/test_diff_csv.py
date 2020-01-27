import unittest
import shutil
import tempfile
from os import path
import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal
from diff_csv.diff_csv import DiffCSV


class TestDiffCSV(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.before_file_path = path.join(self.test_dir, "before.csv")
        before_content = """id1,id2,val1,val2,val3,dummy1,dummy2
1,1,a,b,c,0,asahikawa
1,2,d,e,f,0,asahikawa
2,1,g,h,i,0,asahikawa
3,1,j,k,l,0,asahikawa
"""
        with open(self.before_file_path, "w", encoding="cp932") as f:
            f.write(before_content)

        self.after_file_path = path.join(self.test_dir, "after.csv")
        after_content = """id1,id2,val1,val2,val3,dummy1,dummy2
1,1,a,b,c,1,asahikawa
1,2,d,z,f,2,asahikawa
3,1,j,k,l,3,asahikawa
4,1,o,p,q,4,asahikawa
4,2,r,s,t,5,asahikawa
"""
        with open(self.after_file_path, "w", encoding="cp932") as f:
            f.write(after_content)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_get_differences(self):
        diff_csv = DiffCSV(
            {
                "before_csv": self.before_file_path,
                "after_csv": self.after_file_path,
                "key_cols": [0, 1],
                "except_cols": [5, 6],
            }
        )
        expect = pd.DataFrame(
            {
                0: ["1", "2", "4", "4"],
                1: ["2", "1", "1", "2"],
                "2_after": ["", np.nan, "o", "r"],
                "3_after": ["z", np.nan, "p", "s"],
                "4_after": ["", np.nan, "q", "t"],
                "5_after": ["", "", "", ""],
                "6_after": ["", "", "", ""],
            },
            index=[2, 3, 5, 6],
        )
        assert_frame_equal(expect, diff_csv.differences)

    def test_to_csv(self):
        diff_csv = DiffCSV(
            {
                "before_csv": self.before_file_path,
                "after_csv": self.after_file_path,
                "key_cols": [0, 1],
                "except_cols": [5, 6],
            }
        )
        expect = """1,2,,z,,,
2,1,NaN,NaN,NaN,,
4,1,o,p,q,,
4,2,r,s,t,,
"""
        output_path = path.join(self.test_dir, "output.csv")
        diff_csv.to_csv(output_path)
        with open(output_path, "r", encoding="utf-8") as f:
            result = f.read()
        self.assertEqual(expect, result)


if __name__ == "__main__":
    unittest.main()
