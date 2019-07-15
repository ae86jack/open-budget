import camelot
from abc import ABCMeta, abstractmethod
import pandas as pd
import numpy as np
import re
from typing import List, Tuple
from pprint import pprint
import logging
import os
import click


# @click.command()
# @click.argument('path', default='../../pdf_files/jszwfw', type=click.Path(exists=True))
def run(path):
    """ 解析pdf文件, 把数据导出为csv格式的文件.
    Examples:
    $python pdf_spider.py
    """
    is_all_files = all([os.path.isfile(os.path.join(path, item)) for item in os.listdir(path)])
    if is_all_files:    # 该目录下面都是文件
        dept_name = os.path.basename(path)
        parser = DeptFilesParser(dept_name, path)
        parser.parse()
    else:
        for sub_dir in os.listdir(path):
            dept_name = sub_dir
            print(dept_name)
            parser = DeptFilesParser(dept_name, path + '/' + sub_dir)
            parser.parse()
            break


class DeptFilesParser:
    def __init__(self, dept_name, path):
        self.dept_name = dept_name
        self.path = path
        balance_parser = BalanceParser()

        self.parsers: List[BaseParser] = [balance_parser]

    def parse(self):
        for file in os.listdir(self.path):
            if not file.endswith('.pdf'):
                continue
            print(file)
            year = self._parse_year(file)
            if not year:
                logging.warning(f'{file} 文件名解析不到年度信息')
                continue
            self._parse_file(self.path + '/' + file, year)

        for parser in self.parsers:
            parser.to_csv(self.path)         # 导出csv

    @staticmethod
    def _parse_year(text) -> int:
        p = re.compile('(20[0-9]{2})')      # 2000 - 2099
        result = p.search(text)
        if not result:
            return None
        return int(result.group(1))

    def _parse_file(self, file_path, year):
        tables = camelot.read_pdf(
            file_path, pages='all',
            layout_kwargs={
                'char_margin': 1.0,
                'line_margin': 0.5,
                'word_margin': 0.1,
                'detect_vertical': False
            },
            copy_text=['h'], strip_text='\n',
            flavor='lattice', suppress_stdout=True)

        i, tables_size = 0, len(tables)
        while i < tables_size:
            for parser in self.parsers:
                next_i = parser.parse(tables, i, year)
            if next_i == i:
                print('无法处理该Table', str(tables[i]))
                i = next_i + 1
            else:
                i = next_i


class BaseParser:
    table_name: str = None
    re_digit = re.compile('^[0-9]+\.')
    re_zh_digit = re.compile('^[一二三四五六七八九十]+、')
    re_merge = re.compile('[一二三四五六七八九十]+、')

    def __init__(self):
        self.parsed_df: pd.DataFrame = None

    @abstractmethod
    def has_head(self, df: pd.DataFrame) -> bool:
        """ 检查表的前几行是否符合 """
        pass

    @abstractmethod
    def has_tail(self, df: pd.DataFrame) -> bool:
        """ 检查表的最后几行是否符合 """
        pass

    @abstractmethod
    def parse(self, tables: List[pd.DataFrame], table_index, year):
        """解析, 同时返回下一个的table_index.
        Parameters
        ----------
        tables : List[pd.DataFrame]
        table_index : int, 当前要解析的table_index
        year: int, 年度
        Returns
        -------
        next_index : int. 如果next_index == table_index, 说明解析不成功
        """
        pass

    def correct(self, df: pd.DataFrame):
        max_row, max_col = df.shape
        for index, series in df.iterrows():
            for c, text in series.iteritems():
                is_merge, divided_cells = self.split_merge_cell(text)
                if is_merge:
                    if c >= 1 and df.iloc[index, c - 1] == '':
                        df.iloc[index, c - 1], df.iloc[index, c] = divided_cells
                    elif c <= max_col - 2 and df.iloc[index, c + 1] == '':
                        df.iloc[index, c], df.iloc[index, c + 1] = divided_cells
                    else:
                        logging.warning(f'单位格分开可能出错. df[{index}][{c}] {text}')

    def split_merge_cell(self, text):
        """ 由于camelot在解析table的时候, 会把两个格子的内容合到一起, 所以在这里把它分开.
            比如'24,458.43二、财政专户管理资金' 分为'24,458.43'和'二、财政专户管理资金' """
        if not text or not isinstance(text, str):
            return False, None
        r = self.re_merge.search(text)
        if not r:
            return False, None
        start, end = r.span()
        if start == 0:
            return False, None
        else:
            return True, (text[:start], text[start:])

    def get_df(self, tables: List[pd.DataFrame], table_index) -> Tuple[pd.DataFrame, int]:
        """ 检查是否符合, 如果发现是属于同一个表的, 把它们合并 """
        if not self.has_head(tables[table_index].df):
            return None, table_index
        df: pd.DataFrame = None
        i = table_index
        while i < table_index + 4:  # 最多合并4个table
            if df is None:
                df = tables[i].df
            else:
                df = df.append(tables[i].df, ignore_index=True)
            if self.has_tail(df):
                return df, i + 1
            i += 1
        else:
            # 没有找到
            return None, table_index

    def to_csv(self, path):
        self.parsed_df.to_csv(f'{path}/{self.table_name}.csv')

    def strip(self, word):
        """ 去掉前面的'1.', '一、', 去掉包括空格、制表符、换页符 [ \f\n\r\t\v] """
        if not word or not isinstance(word, str):
            return word
        r1 = self.re_digit.search(word)
        if r1:
            word = word[r1.span()[1]:]
        r2 = self.re_zh_digit.search(word)
        if r2:
            word = word[r2.span()[1]:]
        return re.sub(r'\s+', '', word)

    @staticmethod
    def parse_float(value):
        if not value:
            return None
        try:
            if pd.isna(value):
                return None
            v_f = float(value.replace(',', ''))
            return v_f
        except TypeError:
            return None
        except ValueError:
            return None


class BalanceParser(BaseParser):
    """ 解析收支预算总表 """
    table_name = '收支预算总表'

    def has_head(self, df: pd.DataFrame) -> bool:
        return df.iloc[0, :].equals(pd.Series(['收入', '收入', '支出', '支出', '支出', '支出']))

    def has_tail(self, df: pd.DataFrame):
        return df.iloc[-1, 0] == '收入合计' and df.iloc[-1, 2] == '支出合计'

    def parse(self, tables: List[pd.DataFrame], table_index, year):
        df, next_index = self.get_df(tables, table_index)
        if df is None:
            return next_index

        assert df.iloc[1, :].equals(pd.Series(['项目名称', '金额', '功能分类', '功能分类', '支出用途', '支出用途']))
        assert df.iloc[2, :].equals(pd.Series(['', '', '功能科目名称', '金额', '项目名称', '金额']))
        self.correct(df)

        array, columns = list(), list()
        self.set_data(df, columns, array, 0, 1)
        self.set_data(df, columns, array, 2, 3)
        self.set_data(df, columns, array, 4, 5)

        df_res = pd.DataFrame(np.array([array]), index=[pd.datetime(year=year, month=1, day=1)], columns=columns)
        if self.parsed_df is None:
            self.parsed_df = df_res
        else:
            self.parsed_df = self.parsed_df.append(df_res)
        return next_index

    def set_data(self, df, columns, array, column_title, column_num):
        for i, v in enumerate(df.iloc[:, column_num]):
            num = self.parse_float(v)
            if num:
                columns.append(self.strip(df.iloc[i, column_title]))
                array.append(num)


if __name__ == '__main__':
    run('../../pdf_files/jszwfw/江苏省人大办公厅')
