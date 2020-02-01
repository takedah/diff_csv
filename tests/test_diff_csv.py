import unittest
import shutil
import tempfile
from os import path
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal
from diff_csv.diff_csv import DiffCSV


class TestDiffCSV(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.before_file_path = path.join(self.test_dir, "before.csv")
        before_content = """id1,id2,val1,val2,val3,dummy1,dummy2
1,a,1,b,c,0,asahikawa
1,d,2,e,f,0,asahikawa
2,g,1,h,i,0,asahikawa
3,j,1,k,l,0,asahikawa
"""
        with open(self.before_file_path, "w", encoding="cp932") as f:
            f.write(before_content)

        self.after_file_path = path.join(self.test_dir, "after.csv")
        after_content = """id1,id2,val1,val2,val3,dummy1,dummy2
1,a,1,b,c,1,asahikawa
1,d,2,z,f,2,asahikawa
3,j,1,k,l,3,asahikawa
4,o,1,p,q,4,asahikawa
4,r,2,s,t,5,asahikawa
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
                "key_cols": [0, 2],
                "except_cols": [5, 6],
                "encoding": "cp932",
            }
        )
        expect = pd.DataFrame(
            {
                0: ["1", "2", "4", "4"],
                "1_after": ["", "", "o", "r"],
                2: ["2", "1", "1", "2"],
                "3_after": ["z", "", "p", "s"],
                "4_after": ["", "", "q", "t"],
                "5_after": ["", "", "", ""],
                "6_after": ["", "", "", ""],
                "update_flag": ["update", "delete", "add", "add"],
            },
            index=[2, 3, 5, 6],
        )
        assert_frame_equal(expect, diff_csv.differences)

    def test_to_csv(self):
        diff_csv = DiffCSV(
            {
                "before_csv": self.before_file_path,
                "after_csv": self.after_file_path,
                "key_cols": [0, 2],
                "except_cols": [5, 6],
                "encoding": "cp932",
            }
        )
        expect = """1,,2,z,,,,update
2,,1,,,,,delete
4,o,1,p,q,,,add
4,r,2,s,t,,,add
"""
        output_path = path.join(self.test_dir, "output.csv")
        diff_csv.to_csv(output_path)
        with open(output_path, "r", encoding="utf-8") as f:
            result = f.read()
        self.assertEqual(expect, result)


if __name__ == "__main__":
    unittest.main()
