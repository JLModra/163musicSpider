# -*- coding:utf-8 -*-
'''
Created on 2016年4月26日
算法部分
@author: Modra
'''

from musicSpider import  music_list_info
# from musicSpider import  music_list_info_debug
from musicSpider import  music_list_info_train
from musicSpider import  music_list_info_test
from numpy import *
import time


def split_data():
    music_list_info_train.remove()
    music_list_info_test.remove()
    m = 0
    for i in music_list_info.find():
        if m % 2 == 0:
            music_list_info_test.insert(i)
        else:
            music_list_info_train.insert(i)
        m = m + 1
#     print '分离数据结束'
    
#根据每条歌单的播放次数为歌单贴标签    
def classify(music_list_info):
    num_first = 0
    num_second = 0
    num_third = 0
    for i in music_list_info.find():
        list_id = i['_id']
        play_count = int(i['play_count'])
        classification = -100
        if (play_count <= 1000):
            classification = -1
            num_first = num_first + 1
        elif (play_count > 1000 and play_count <= 10000):
            classification = 0
            num_second = num_second + 1
        else:
            classification = 1
            num_third = num_third + 1
        music_list_info.update({"_id" : list_id},{"$set" : {'classification' : classification}})
    return num_first, num_second, num_third    
        
def clean_data(music_list_info):
    for i in music_list_info.find():
        list_id = i['_id']
        play_count = int(i['play_count'])
        if play_count <= 50:
            music_list_info.remove({"_id" : list_id})
            

#用单层决策树训练adaboost
def adaboost_train_DS(num):
    #弱分类器集合
    weak_class_arr = []
    #导入每条纪录的标签
    classification_map = {}
    #每条数据的权值
    weight_map = {}
    #存储最后加权得到的结果
    result = {}
    for i in music_list_info_train.find():
        classification_map[i['_id']] = i['classification']
        weight_map[i['_id']] = 1.0 / music_list_info_train.count()
        result[i['_id']] = 0
    for m in range(num):
        best_stump = build_decision_stump(10, classification_map, weight_map)
        #计算alpha值
#         alpha = float(0.5*log((1.0-best_stump['err'])/max(best_stump['err'],1e-16)))
#         alpha = float(log(max(best_stump['err'],1e-16) / (1.0-best_stump['err']))) + log(2)
        alpha = float(0.5*log((1.0-best_stump['err'])/max(best_stump['err'],1e-16))) + log(2)
        #若分类器正确分类，此时权值的乘积
        true_d = exp(-1*alpha)
        #若分类器错误分类，此时权值的乘积
        false_d = exp(1*alpha)
        best_stump['alpha'] = alpha
        print '第' , m , '次循环' , 'alpha：' , alpha
        print '第' , m , '次循环' , 'feature：' , best_stump['feature']
        print '第' , m , '次循环' , 'true_d：' , true_d
        print '第' , m , '次循环' , 'false_d：' , false_d
        print '第' , m , '次循环' , 'err1：' , best_stump['err1']
        print '第' , m , '次循环' , 'err2：' , best_stump['err2']
        print '第' , m , '次循环' , 'err3：' , best_stump['err3']
        print '第' , m , '次循环' , 'err：' , best_stump['err']
        print '第' , m , '次循环' , 'flag1：' , best_stump['flag1']
        print '第' , m , '次循环' , 'flag2：' , best_stump['flag2']
#         print '第' , m , '次循环' , '最佳树：' , best_stump
#         print '第' , m , '次循环' , '训练标签：' , classification_map
        #打印出每次循环的权值
#         print '第' , m , '次循环' , '权值：' , weight_map
        #把训练出的弱分类器收集起来
        weak_class_arr.append(best_stump)
        #纪录每个分类器的分类结果
        result_temp = {}
        feature_map = {}
        for i in  music_list_info_train.find():
            feature_map[i['_id']] = i[str(best_stump['feature'])]
#         print '第' , m , '次循环' , 'feature_map：' , feature_map
#         print '第' , m , '次循环' , 'list1：' , best_stump['list1']
#         print '第' , m , '次循环' , 'list2：' , best_stump['list2']
#         print '第' , m , '次循环' , 'list3：' , best_stump['list3']
        for i in feature_map.keys():
            feature = int(feature_map[i])
            flag1 = best_stump['flag1']
            flag2 = best_stump['flag2']
            classification = best_stump['classification']
            if feature < flag1:
                result_temp[i] = classification[0]
                result[i] = result[i] + alpha * classification[0]
                if classification_map[i] == classification[0]:
                    weight_map[i] = weight_map[i] * true_d  
                else:
                    weight_map[i] = weight_map[i] * false_d
            elif feature >= flag1 and feature <= flag2:
                result_temp[i] = classification[1]
                result[i] = result[i] + alpha * classification[1]
                if classification_map[i] == classification[1]:
                    weight_map[i] = weight_map[i] * true_d  
                else:
                    weight_map[i] = weight_map[i] * false_d
            else:
                result_temp[i] = classification[2]
                result[i] = result[i] + alpha * classification[2]
                if classification_map[i] == classification[2]:
                    weight_map[i] = weight_map[i] * true_d      
                else:
                    weight_map[i] = weight_map[i] * false_d
        weight_all = 0
        for weight in weight_map.values():
            weight_all = weight_all + weight
        for i in weight_map.keys():
            weight_map[i] = weight_map[i]/weight_all
#         print '每个分类器的分类结果' , result_temp
#         print '加权结果' , result
        result_about = {}
        for i in result.keys():
            if result[i] < -1:
                result_about[i] = -1
            elif result[i] >= -1 and result[i] <= 1:
                result_about[i] = 0
            else:
                result_about[i] = 1
        err_num = 0
        for i in result_about:
            music_list_info_train.update({"_id" : i},{"$set" : {'result_about' : result_about[i]}})
            music_list_info_train.update({"_id" : i},{"$set" : {'result' : result[i]}})
            music_list_info_train.update({"_id" : i},{"$set" : {'result_temp' : result_temp[i]}})
            if result_about[i] != classification_map[i]:
                err_num = err_num + 1
        err_num_rate = err_num * 1.0 / len(result_about)
#         print '训练拟合错误率：' , err_num_rate
        if err_num_rate == 0:
            break
    return weak_class_arr

def adaboost_classify_2(classifier_arr):
    err_num = 0
    result = {}
    result_about = {}
    for i in music_list_info_test.find():
        result[i['_id']] = 0
    classification_map = {}
    for i in music_list_info_test.find():
        classification_map[i['_id']] = i['classification']
    for i in classifier_arr:
        alpha = i['alpha']
        feature = i['feature'] 
        flag1 = i['flag1']
        flag2 = i['flag2']
        classification = i['classification']
        feature_map = {}
        for m in music_list_info_test.find():
            feature_map[m['_id']] = str(m[feature])
        for i in feature_map.keys():
            if feature_map[i] < flag1:
                result[i] = result[i] + alpha * classification[0]
            elif feature_map[i] >= flag1 and feature_map[i] <= flag2:
                result[i] = result[i] + alpha * classification[0]
            else:
                result[i] = result[i] + alpha * classification[0]
        for i in result.keys():
            if result[i] < -1:
                result_about[i] = -1
            elif result[i] >= -1 and result[i] <= 1:
                result_about[i] = 0
            else:
                result_about[i] = 1
    for i in result_about:
        music_list_info_test.update({"_id" : i},{"$set" : {'result_about_nihe' : result_about[i]}})
        music_list_info_test.update({"_id" : i},{"$set" : {'result_nihe' : result[i]}})
        if result_about[i] != classification_map[i]:
            err_num = err_num + 1
    return err_num * 1.0 / len(classification_map)
    
def adaboost_classify(classifier_arr, music_list):
    first_first = 0
    first_second = 0
    first_third = 0
    second_first = 0
    second_second = 0
    second_third = 0
    third_first = 0
    third_second = 0
    third_third = 0
    classification_map = {}
    classification_result = {}
    err_num = 0
    for l in music_list.find():
        classification_result[l['_id']] = []
    for i in classifier_arr:
        feature = i['feature'] 
        flag1 = i['flag1']
        flag2 = i['flag2']
        classification = i['classification']
        feature_map = {}
        for m in music_list.find():
            feature_map[m['_id']] = str(m[feature])
        for n in feature_map.keys():
            feature_temp = int(feature_map[n])
            if feature_temp < flag1:
                classification_result[n].append(classification[0])
            elif feature_temp >= flag1 and feature_temp <= flag2:
                classification_result[n].append(classification[1])
            else:
                classification_result[n].append(classification[2])
    for i in classification_result.keys():
        music_list.update({"_id" : i},{"$set" : {'result_toupiao_list' : classification_result[i]}})
        result_arr = classification_result[i]
        classification_one_num = 0
        classification_two_num = 0
        classification_three_num = 0
        for m in result_arr:
            if m == -1:
                classification_one_num = classification_one_num + 1
            elif m == 0:
                classification_two_num = classification_two_num + 1
            else:
                classification_three_num = classification_three_num + 1
        if classification_one_num >= classification_two_num and classification_one_num >= classification_three_num:
            classification_result[i] = -1
        elif classification_two_num >= classification_one_num and classification_two_num >= classification_three_num:
            classification_result[i] = 0  
        else:
            classification_result[i] = 1
    for i in music_list.find():
        classification_map[i['_id']] = i['classification']
    for i in classification_map.keys():
        music_list.update({"_id" : i},{"$set" : {'result_toupiao' : classification_result[i]}})
        music_list_info.update({"_id" : i},{"$set" : {'result_toupiao' : classification_result[i]}})
        if classification_map[i] != classification_result[i]:
            err_num = err_num + 1
            if classification_map[i] == -1:
                if classification_result[i] == 0:
                    first_second = first_second + 1
                else:
                    first_third = first_third + 1
            elif classification_map[i] == 0:
                if classification_result[i] == -1:
                    second_first = second_first + 1
                else:
                    second_third = second_third + 1
            else:
                if classification_result[i] == -1:
                    third_first = third_first + 1
                else:
                    third_second = third_second + 1
        else:
            if classification_map[i] == -1:
                first_first = first_first + 1
            elif classification_map[i] == 0:
                second_second = second_second + 1
            else:
                third_third = third_third + 1
            
    return err_num * 1.0 / len(classification_result), first_first, first_second, first_third, second_first, second_second, second_third, third_first, third_second, third_third
        
                     
                     
 
#建立单层三枝决策树
#参数：步数，便签map，权值map
def build_decision_stump(num_steps, classification_map, weight_map):
    start = time.time()
    #最佳树
    best_stump = {}
    #flag1和flag2是两个结点，用来把数据分为三块
    flag1 = 0
    flag2 = 0
    #错误率
    min_err = inf
    #features_map是id-feature的映射
    features_map = {}
    #classification_list是可能的classification值的list
    classification_list = [[1, -1, 0], [1, 0, -1], [-1, 1, 0], [-1, 0, 1], [0, 1, -1], [0, -1, 1]]
    #需要遍历的特征
    #介绍、歌曲数、标签、
    features = ['introduce', 'count', 'tags', 'owner_music_list_num', 'owner_listen_music_num', 'owner_fan_num', 'owner_collect_music_list_num', 'score']
    #遍历所有的特征
    for feature in features:
        #遍历数据库
        for i in music_list_info_train.find():
            #从数据库中取到该特征的值
            features_map[i['_id']] = int(i[feature])
        #取到某个特征样本两边的极点即最大最小值
        min_num = max_num = features_map.values()[0]
        for i in features_map.values():
            if i < min_num :
                min_num = i
            if i > max_num :
                max_num = i
        #计算步长
        step_size = 1.0*(max_num - min_num)/num_steps
#         print 'step_size:' , step_size
#         print 'num_steps:' , num_steps
        for m in range(num_steps):
            for n in range(num_steps - m - 1):
                flag1 = step_size * m + min_num
                flag2 = (n + 1) * step_size + flag1
                for classification in classification_list:
                    list1 = []
                    list2 = []
                    list3 = []
                    for i in features_map:
                        if features_map[i] < flag1:
                            list1.append(i)
                        elif features_map[i] >= flag1 and features_map[i] <= flag2:
                            list2.append(i)
                        else:
                            list3.append(i)
#                     list1_debug = []
#                     list2_debug = []
#                     list3_debug = []
#                     for x in features_map.keys():
#                         for y in list1:
#                             if (x == y):
#                                 list1_debug.append(features_map[y])
#                         for y in list2:
#                             if (x == y):
#                                 list2_debug.append(features_map[y])
#                         for y in list3:
#                             if (x == y):
#                                 list3_debug.append(features_map[y])
                    weighted_error, err1, err2, err3 = cal_err(classification, list1, list2, list3, classification_map, weight_map)
                    #print '当前feature:' , feature , '当前m:' , m , '当前n:' , n , 'min:' , min_num , 'max:' , max_num , '当前flag1:' , flag1 , '当前flag2:' , flag2 , 'list1' , list1_debug , 'list2' , list2_debug , 'list3' , list3_debug , 'classification:' , classification , 'err:' , weighted_error , 'weight:' , weight_map.values() , 'classification_map:' , classification_map
                    
                    #打印调试信息
                    #print '当前的特征：'  , feature , 'min:' , min_num , 'max:' , max_num , 'flag1:' , flag1 , 'flag2:' , flag2 , 'classification:' , classification , 'err:' , weighted_error
                    if weighted_error < min_err:
                        min_err = weighted_error
                        best_stump['flag1'] = flag1
                        best_stump['flag2'] = flag2
                        best_stump['classification'] = classification
                        best_stump['err'] = min_err
                        best_stump['err1'] = err1
                        best_stump['err2'] = err2
                        best_stump['err3'] = err3
                        best_stump['feature'] = feature 
#                         best_stump['list1'] = list1_debug
#                         best_stump['list2'] = list2_debug
#                         best_stump['list3'] = list3_debug
    end = time.time()
    print '训练一棵单层决策树时间：' , end - start
    return best_stump
    
        

#计算某种特征向量的错误率 
def cal_err(classification, id_list1, id_list2, id_list3, classification_map, weight_map):
    err1 = 0
    err2 = 0
    err3 = 0
    for i in id_list1:
        if classification_map[i] != classification[0]:
            err1 = err1 + weight_map[i]
    
    for i in id_list2:
        if classification_map[i] != classification[1]:
            err2 = err2 + weight_map[i]
    
    for i in id_list3:
        if classification_map[i] != classification[2]:
            err3 = err3 + weight_map[i]
    
    err = err1 + err2 + err3
    return err, err1, err2, err3
    
if __name__ == "__main__": 
    start = time.time() 
    clean_data(music_list_info)
    num_first, num_second, num_third = classify(music_list_info)
#     print 'num1:' , num_first
#     print 'num2:' , num_second
#     print 'num3:' , num_third
    split_data()
    classifier_arr = adaboost_train_DS(10)
    err_rate_test, first_first_test, first_second_test, first_third_test, second_first_test, second_second_test, second_third_test, third_first_test, third_second_test, third_third_test = adaboost_classify(classifier_arr, music_list_info_test)
    err_rate_train, first_first_train, first_second_train, first_third_train, second_first_train, second_second_train, second_third_train, third_first_train, third_second_train, third_third_train = adaboost_classify(classifier_arr, music_list_info_train)
    print '训练错误率：' , err_rate_train
    print 'first_first:' , first_first_test
    print 'first_second:' , first_second_test
    print 'first_third:' , first_third_test
    print 'second_first:' , second_first_test
    print 'second_second:' , second_second_test
    print 'second_third:' , second_third_test
    print 'third_first:' , third_first_test
    print 'third_second:' , third_second_test
    print 'third_third:' , third_third_test
#     print '训练投票错误率err-1：' , err_num_first_train * 1.0 / num_first
#     print '训练投票错误率err0：' , err_num_second_train * 1.0 / num_second
#     print '训练投票错误率err1：' , err_num_third_train * 1.0 / num_third
    print '测试错误率：' , err_rate_test
#     print '测试投票错误率err-1：' , err_num_first_test * 1.0 / num_first
#     print '测试投票错误率err0：' , err_num_second_test * 1.0 / num_second
#     print '测试投票错误率err1：' , err_num_third_test * 1.0 / num_third
    err_rate = adaboost_classify_2(classifier_arr)
#     print '测试拟合错误率：' , err_rate
    end = time.time()
    print '算法总时间：' , end - start
    
            






