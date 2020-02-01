import pandas as pd
import numpy as np
import re


class DiffCSV:
    """2つのCSVを比較し、変更があった部分のみを出力する。

    Attributes:
        differences (:obj:`pandas.DataFrame`): 2つのCSVの差の部分を抽出したデータ。
    """

    def __init__(self, args: dict):
        """
        Args:
            args["before_csv"] (str): 変更前のCSVファイルのパス。
            args["after_csv"] (str): 変更後のCSVファイルのパス。
            args["key_cols"] (list): 比較するキーとするカラムの番号のリスト。デフォルトは0のみのリスト。
            args["except_cols"] (list): 抽出から除外するカラムの番号のリスト。デフォルトは空リスト。
            args["encoding"] (str): CSVファイルのエンコード。デフォルトはUTF-8。

        """

        self.__before_csv_path = args["before_csv"]
        self.__after_csv_path = args["after_csv"]
        self.__key_cols = args.get("key_cols", [0])
        self.__except_cols = args.get("except_cols", [])
        self.__encoding = args.get("encoding", "utf-8")
        self.__differences = self._get_differences()

    @property
    def differences(self):
        return self.__differences

    def to_csv(self, file_path):
        """抽出した変更箇所をCSVファイルに出力する。

        Args:
            file_path (str): 出力するCSVファイルのパス。

        Returns:
            bool: 成功したら真を返す。
        """
        self.__differences.to_csv(
            file_path, header=False, index=False, encoding=self.__encoding
        )
        return True

    def _get_differences(self):
        """2つのCSVファイルを比較して変更箇所を抽出する。

        Returns
        -------
        differences (:obj:`pandas.DataFrame`): CSVの差分。

        """

        before_csv = pd.read_csv(
            self.__before_csv_path, header=None, encoding=self.__encoding, dtype=str
        )
        after_csv = pd.read_csv(
            self.__after_csv_path, header=None, encoding=self.__encoding, dtype=str
        )
        df = pd.merge(
            before_csv,
            after_csv,
            how="outer",
            on=self.__key_cols,
            indicator=True,
            suffixes=["_before", "_after"],
        )
        df["update_flag"] = "none"
        df.replace(np.nan, "", inplace=True)

        concat_column_names = df.columns.values.tolist()
        before_column_names = [
            s for s in concat_column_names if str(s).endswith("_before")
        ]
        after_column_names = [
            s for s in concat_column_names if str(s).endswith("_after")
        ]
        if self.__except_cols != []:
            except_col_names = list(
                map(lambda x: str(x) + "_before", self.__except_cols)
            )
        else:
            except_col_names = []
        for index, row in df.iterrows():
            i = 0
            while i < len(before_column_names):
                if before_column_names[i] in except_col_names:
                    df.at[index, after_column_names[i]] = ""
                else:
                    before_value = row[before_column_names[i]]
                    after_value = row[after_column_names[i]]
                    if before_value == after_value:
                        df.at[index, after_column_names[i]] = ""
                    else:
                        df.at[index, "update_flag"] = "update"
                i += 1
            if row["_merge"] == "left_only":
                df.at[index, "update_flag"] = "delete"
            elif row["_merge"] == "right_only":
                df.at[index, "update_flag"] = "add"

        i = 0
        for col_name in after_column_names:
            i += 1

        output_cols = self._sort_column_names(self.__key_cols, after_column_names)
        return df[output_cols][df["update_flag"] != "none"]

    @staticmethod
    def _sort_column_names(key_cols, after_column_names):
        """
        元のCSVファイルのカラムと同じ順でCSVを出力させるため、データフレームのカラム名を取得し、
        並べ替えた後のカラム名のリストを返す。
        データフレームをマージするための主キーとしたカラムにsuffixが付かないことと、
        文字列の数値を並べ替えることが、単純にリストのsortメソッドではうまくいかないため。

        Args:
            key_cols (list of int): 主キーとしたカラム番号のリスト。
            column_names (list of str): データフレームのカラム名のリスト。

        Returns:
            sorted_column_names (list): ソート後のカラム名のリスト。

        """

        sorted_column_names = list()
        i = 0
        while i < len(key_cols + after_column_names):
            if i in key_cols:
                sorted_column_names.append(i)
                i += 1
                continue
            for col_name in after_column_names:
                if i == int(re.search(r"^\d+", col_name).group()):
                    sorted_column_names.append(col_name)
                    i += 1
                    continue
        sorted_column_names.append("update_flag")
        return sorted_column_names
