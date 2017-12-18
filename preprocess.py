import numpy as np
from PCA.pca import *

PCA = {'0.85':187, '0.9':453}

# 合并疾病各阶段
def merge_disease(label_dic, origin_num, annos):
    disease = ["Huntington's Disease (HD) Pathological",
               "lung adenocarcinoma (NCI_Thesaurus C0152013) has DiseaseStaging"]

    for dis in disease:
        origin_num[dis] = []
        label_dic[dis] = 0
        rubbish_key = []

        for k in label_dic:
            if dis in k and dis != k:
                label_dic[dis] += label_dic[k]
                origin_num[dis] += origin_num[k]
                rubbish_key.append(k)

        for k in rubbish_key:
            label_dic.pop(k)
            origin_num.pop(k)

        for i in range(len(annos)):
            if dis in annos[i]:
                annos[i] = dis

    return label_dic, origin_num, annos

# 提取出出现次数>=10次的疾病，返回相应基因芯片数据的序号
def look_anno():
    fin = open('data/E-TABM-185.sdrf.txt', 'r')         # 标注数据
    fout = open('output/data/data_processed.txt', 'w')  # 相应疾病对应原始数据的编号
    fout_anno = open('output/data/anno_processed.txt', 'w')

    s = fin.readline()
    annos = []
    label_dic = {}  # 各疾病出现的次数
    origin_num = {} # 存下基因芯片编号

    # 读标注
    for i in range(5896):
        s = fin.readline()
        l = s.split('\t')
        annos.append(l[7])
        if l[7] != '  ':
            if l[7] in label_dic:
                label_dic[l[7]] += 1
            else:
                label_dic[l[7]] = 1

            if l[7] in origin_num:
                origin_num[l[7]].append(i)
            else:
                origin_num[l[7]] = []
                origin_num[l[7]].append(i)

    label_dic, origin_num, annos = merge_disease(label_dic, origin_num, annos)

    # 删去出现次数少的疾病
    for k in label_dic:
        if label_dic[k] > 9:
            fout.write(k + '\t' + str(origin_num[k]) + '\n')
        else:
            origin_num.pop(k)

    # 排序，此时字典变list
    label_dic = sorted(label_dic.items(), key=lambda item: item[0])
    origin_num = sorted(origin_num.items(), key=lambda item: item[0])

    # 标注顺序重组
    for k in origin_num:
        for num in k[1]:
            fout_anno.write(str(annos[num]) + '\n')

    fin.close()
    fout.close()
    fout_anno.close()

    # '''for test'''
    # ftest = open('output/data/label_dic.txt', 'w')    # 各疾病出现次数
    # n = 0
    # for dd in label_dic:
    #     ftest.write("%-80s" % dd[0] + str(dd[1]) + '\n')
    #     if dd[1] > 9:
    #         n += 1
    # print('all diseases appear more than 10 times: %d' %n)
    # print('origin num:\n', origin_num)
    # ftest.close()

    return origin_num

def look_rawdata(origin_num):
    fin = open('data/microarray.original.txt', 'r')
    lines = []
    fin.readline()
    pca_percentage = 0.9
    fout = open('output/pca/pca%f.txt' % round(pca_percentage, 2), 'w')
    dataset_np = np.zeros([3558, PCA[str(pca_percentage)]])

    # read raw data
    for i in range(22283):
        line = fin.readline()
        line = line.split('\t')
        line = line[1:]
        lines.append(list(map(float, line)))

    print("Data has been read successfully.")

    # do PCA
    data = np.array(lines).T
    print("Now reducing dimension...")
    print(data[0][0])
    lowDData = pca(data, pca_percentage)
    print(lowDData[0][0])
    print("Finished, the new dimension is :" + str(len(lowDData[0])))

    # save results (.txt file and .npy)
    print("Start writing new data...")
    for k in origin_num:
        for num in k[1]:
            for i in range(len(lowDData[num])):
                dataset_np[num][i] = lowDData[num][i]
                fout.write(str(lowDData[num][i]) + '\t')
            fout.write('\n')
    np.save('output/data/dataset.npy')
    print("Finished the whole work.")

    fin.close()
    fout.close()

def anno2classes():
    fin = open('output/data/anno_processed.txt', 'r')
    fout = open('output/data/classes_label.txt', 'w')
    target_np = np.zeros([3558, 76, 1])

    annos = fin.readlines()
    n = 0
    fout.write(str(n) + '\n') # first disease should be class 0
    target_np[0][0][0] = 1
    for i in range(1, len(annos)):
        if annos[i] != annos[i - 1]:
            n += 1
        fout.write(str(n) + '\n')
        target_np[i][n][0] = 1

    fin.close()
    fout.close()
    np.save('output/data/target.npy', target_np)

if __name__ == '__main__':
    origin_num = look_anno()
    look_rawdata(origin_num)
    anno2classes()
