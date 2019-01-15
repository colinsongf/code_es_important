#!/usr/bin/python
# -*- coding: UTF-8 -*-

#xls文件向csv文件转化

import pandas as pd
import sys

def xlsx_to_csv_pd(filename):
    data_xls = pd.read_excel(filename, index_col=0)
    nfilename = filename[0:filename.rfind('.')]
    data_xls.to_csv(nfilename+'.csv', encoding='utf-8')


if __name__ == '__main__':
    input_text = sys.argv[1]
    xlsx_to_csv_pd(input_text)

