diff_csv
========

You can extract only different elements between two CSV files which have the same structure by this module.

When comparing files, you can select multiple key columns to connect two CSV files.

You can also select specific columns to exclude from this comparision.

レイアウトが同じ2つのCSVファイルを比較し、値が更新された要素のみを抽出できるものが欲しくて作りました。

複数のカラムをキーにCSVファイルの各行を比較できるようになっています。

また、特定の列は比較対象から除外することもできるようになっています。

# Requirement

- pandas
- numpy

# Usage

before.csv

```
id,col1,col2,col3
1,abc,def,ghi
2,jkl,mno,pqr
3,stu,vwx,yz1
```

after.csv

```
id,col1,col2,col3
1,abc,def,ghi
2,jkl,MNO,pqr
4,234,567,890
5,ABC,DEF,GHI
```

Sample code is below.

```
from diff_csv.diff_csv import DiffCSV

diff = DiffCSV(
    {
        "before_csv": 'before.csv',
        "after_csv": 'after.csv',
        "key_cols": [0],
    }
)
print(diff.diffrences)
```

Outputs are below. (pandas DataFrame)

```
.   0 1_after 2_after 3_after 4_after update_flag
2         MNO             update
3                         delete
4  234    567     890     add
5  ABC    DEF     GHI     add
```

You can output differences to CSV.

```
diff.to_csv('output.csv')
```

# Author

- Hiroki Takeda
- takedahiroki@gmail.com

# Linsence

diff_csv is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
