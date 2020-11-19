# date : 2020/11/19
# 시뮬레이션에 사용하는 utilities
#
# 보다 자세한 내용을 아래 tistory 참고
# https://money-expert.tistory.com/34
#
import json
import csv

#
# for read data from cvs
#
# row : value list
def get_new_item(keys, row) :
    data = {}
    for i in range(len(row)) :
        data[keys[i]] = row[i]
    return data

# 첫 줄은 title이라고 가정, 이후에 title 값을 key로 갖는 dict로 읽기
def read_csv_to_dict(fname) :
    data = []
    keys =[]
    first = 1
    with open(fname, 'r', encoding='UTF8') as FILE :
        csv_reader = csv.reader(FILE, delimiter=',', quotechar='"')
        for row in csv_reader :
            if first : # make dict keys
                keys = row.copy()
#                for key in row :
#                    keys .append(key)
                first = 0
            else :                
                data.append(get_new_item(keys, row))
    return data

#
# for writing data to cvs format
#
def save_to_file_csv(file_name, data) :
    with open(file_name,'w',encoding="cp949") as make_file: 
        # title 저장
        vals = data[0].keys()
        ss = ''
        for val in vals:
            val = val.replace(',','')
            ss += (val + ',')
        ss += '\n'
        make_file.write(ss)

        for dt in data:
            vals = dt.values()
            ss = ''
            for val in vals:
                sval = str(val) 
                sval = sval.replace(',','')
                ss += (sval + ',')
            ss += '\n'
            make_file.write(ss)
    make_file.close()

if __name__ == '__main__':

    print('myutil')
