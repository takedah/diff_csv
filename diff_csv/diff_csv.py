import pandas as pd


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

        """

        self.__before_csv_path = args["before_csv"]
        self.__after_csv_path = args["after_csv"]
        self.__key_cols = args.get("key_cols", [0,])
        self.__except_cols = args.get("except_cols", [])
        self.__differences = self._get_differences()

    @property
    def differences(self):
        return self.__differences

    def _get_differences(self):
        """2つのCSVファイルを比較して変更箇所を抽出する。

        Returns
        -------
        differences (:obj:`pandas.DataFrame`): CSVの差分。

        """

        before_csv = pd.read_csv(self.__before_csv_path, header=None)
        after_csv = pd.read_csv(self.__after_csv_path, header=None)
        df = pd.merge(
            before_csv,
            after_csv,
            how="outer",
            on=self.__key_cols,
            indicator=True,
            suffixes=["_before", "_after"],
        )
        df["update_flag"] = "none"

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

        output_cols = self.__key_cols + after_column_names
        output_cols.sort(key=str)
        return df[output_cols][df["update_flag"] != "none"]
