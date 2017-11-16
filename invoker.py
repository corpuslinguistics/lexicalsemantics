# -*- coding: utf8 -*-

import collections
import ConfigParser
import gensim
import logging
import os
import platform
import re
import sys

if platform.system() == 'Windows':
    delimiter = '\\'
elif platform.system() == 'Darwin' or platform.system() == 'Linux':
    delimiter = '/'

config_parser = ConfigParser.ConfigParser()
config_parser.read(delimiter.join([sys.path[0], 'config.txt']))

def count_word(file_name):
    f = open(file_name)
    words_box = list()
    for line in f:                         
        line = line.decode('utf8').strip()
        words_box.extend(line.split())               
    f.close()
    
    return collections.Counter(words_box)

def group_by_entity_type():
    file_dict = dict()
    entity_type_set = set()
    f = open('TCMSem_full.txt')
    for line in f:
        line = line.decode('utf8').strip()
        item_list = line.split('\t')
        for item in item_list:
            item = item.strip() 
        if item_list[1] not in entity_type_set:
#             print item_list[1]
            entity_type_set.add(item_list[1])
            file_dict[item_list[1]] = open('entity_type/TCMSem_' + item_list[1] + '.txt', 'w')
        file_dict[item_list[1]].write(item_list[0].encode('utf8') + '\t' + item_list[2].encode('utf8') + '\t' + item_list[5].encode('utf8') + '\n')
        if item_list[3] not in entity_type_set:
#             print item_list[3]
            entity_type_set.add(item_list[3])
            file_dict[item_list[3]] = open('entity_type/TCMSem_' + item_list[3] + '.txt', 'w')
        file_dict[item_list[3]].write(item_list[0].encode('utf8') + '\t' + item_list[2].encode('utf8') + '\t' + item_list[5].encode('utf8') + '\n')

    for value in file_dict.values():
        value.close()        
    f.close()
    
    return entity_type_set

def group_by_relation_type():
    file_dict = dict()
    relation_type_set = set()
    f = open('TCMSem_full.txt')
    for line in f:
        line = line.decode('utf8').strip()
        item_list = line.split('\t')
        for item in item_list:
            item = item.strip()
        item_list[4] = re.sub('[^ a-zA-Z]','', item_list[4]).lower()
        if item_list[4] not in relation_type_set:
#             print item_list[1]
            relation_type_set.add(item_list[4])
            file_dict[item_list[4]] = open('relation_type/TCMSem_' + item_list[4] + '.txt', 'w')
        file_dict[item_list[4]].write(item_list[0].encode('utf8') + '\t' + item_list[2].encode('utf8') + '\t' + item_list[5].encode('utf8') + '\n')

    for value in file_dict.values():
        value.close()        
    f.close()
    
    return relation_type_set


def group_by_frequency():
    word_count_dict = count_word('700_token_1l.txt')

    word_set = set()
    word_list = list()
    frequency_list = list()
    count_list = list()
    f = open('TCMSem.txt')
    f_out_low = open('TCMSem_low.txt', 'w')
    f_out_high = open('TCMSem_high.txt', 'w')
    f_out_low_high = open('TCMSem_low_high.txt', 'w')
    for line in f:
        line = line.decode('utf8').strip()
        item_list = line.split()
        for item in item_list[:2]:
            if item not in word_set:
                word_list.append(item)
                frequency_list.append(word_count_dict[item])
                count_list.append(word_count_dict[item] / 100)
            word_set.add(item)
        
        if word_count_dict[item_list[0]] < 1000 and word_count_dict[item_list[1]] < 1000:
            # low, low
            f_out_low.write(line.encode('utf8') + '\n')
        elif word_count_dict[item_list[0]] >= 1000 and word_count_dict[item_list[1]] >= 1000:
            # high, high
            f_out_high.write(line.encode('utf8') + '\n')
        else:
            f_out_low_high.write(line.encode('utf8') + '\n')
        
    f_out_low.close()
    f_out_high.close()
    f_out_low_high.close()
    f.close()
    
    print len(word_set)
    print len(frequency_list)
#     for i in xrange(len(word_list)):
#         print word_list[i] + '\t' + str(frequency_list[i])
    print count_list
    print collections.Counter(count_list)
    
# a memory-friendly iterator
class MySentences(object):
    def __init__(self, path_name):
        self.path_name = path_name

    def __iter__(self):
        for fname in os.listdir(self.path_name):
            if not fname.startswith('.') and not os.path.isdir(os.path.join(self.path_name, fname)):
                for line in open(os.path.join(self.path_name, fname)):
                    yield line.decode('utf8').split()
                    
def train():
    try:
        print u'正在训练......'

        sentences = MySentences(delimiter.join([sys.path[0], config_parser.get(platform.system(), 'corpus')]))

        # See http://radimrehurek.com/gensim/models/word2vec.html for details
        # Defaults: 
        # sentences=None, size=100, alpha=0.025, window=5, min_count=5, max_vocab_size=None, 
        # sample=0.001, seed=1, workers=3, min_alpha=0.0001, sg=0, hs=0, negative=5, cbow_mean=1, 
        # hashfxn=<built-in function hash>, iter=5, null_word=0, trim_rule=None, sorted_vocab=1, 
        # batch_words=10000
        model = gensim.models.Word2Vec(sentences, sg=1, hs=1, size=64)
        
#         bigram_transformer = gensim.models.Phrases(sentences)
#         model = gensim.models.word2vec.Word2Vec(bigram_transformer[sentences], sg=1, hs=1, size=64)

        model.save(delimiter.join([sys.path[0], config_parser.get(platform.system(), 'pkl')]))
        model.wv.save_word2vec_format(delimiter.join([sys.path[0], config_parser.get(platform.system(), 'bin')]), binary=True)
        model.wv.save_word2vec_format(delimiter.join([sys.path[0], config_parser.get(platform.system(), 'txt')]), binary=False)
            
        print u'训练成功'
    except Exception as e:
        print e
        print u'训练失败'

def query():
    try:
        print u'正在加载模型......'

        model = gensim.models.Word2Vec.load(delimiter.join([sys.path[0], config_parser.get(platform.system(), 'pkl')]))
    
        while True:
            print u'输入1个词查找相似词，例如“茯苓”；'
            print u'输入2个词计算相似度，例如“茯苓 白术”；'
            print u'输入3个词查找与第3个词具备前2个词类似关系的词，例如“陈皮 化痰 牛黄”：'
            
            keyword_list = raw_input().decode(config_parser.get(platform.system(), 'encoding')).split()
            logging.debug(len(keyword_list))
        
            if len(keyword_list) == 0:
                return
            if len(keyword_list) == 1:
                for item in model.most_similar(keyword_list[0]):
                    print item[0]
                    print item[1]
            if len(keyword_list) == 2:
                print model.similarity(keyword_list[0], keyword_list[1])
            if len(keyword_list) == 3:
                for item in model.most_similar(positive=[keyword_list[0], keyword_list[1]], negative=[keyword_list[2]]):
                    print item[0]
                    print item[1]
    except Exception as e:
        print e

def query_in_batch():
    try:
        print u'正在加载模型......'

        model = gensim.models.Word2Vec.load(delimiter.join([sys.path[0], config_parser.get(platform.system(), 'pkl')]))
        
        input_file = file(config_parser.get(platform.system(), 'query'))
        output_file = file(config_parser.get(platform.system(), 'similar'), 'w')
        for line in input_file:
            line = line.decode('utf8').strip()
            if len(line) == 0:
                continue
                
            try:
                output_file.write(line.encode('utf8') + '\t')
                for item in model.most_similar(line):
                    output_file.write(item[0].encode('utf8') + '\t' + str(item[1]) + '\t')
            except KeyError as e:
#                 print e
                continue
            finally:
                output_file.write('\n')
        input_file.close()
        
        print u'查询成功'
    except Exception as e:
        print e
        print u'查询失败'

def phrase():
    print u'正在生成短语......'
    
    sentences = MySentences(delimiter.join([sys.path[0], config_parser.get(platform.system(), 'corpus')]))

    phrases = gensim.models.Phrases(sentences, delimiter='')

    f = open(delimiter.join([sys.path[0], config_parser.get(platform.system(), 'phrase')]), 'w')
    for sentence in list(phrases[sentences]):
        f.write('\t'.join(sentence).encode('utf8') + '\n')
    f.close()
    
    print u'生成短语成功'
            
def main():
    try:
        if sys.argv[1].startswith('-'):
            option = sys.argv[1][1:]
            if option == 'train':
                train()
            if option == 'query':
                query()
            if option == 'query_in_batch':
                query_in_batch()
#             if option == 'phrase':
#                 phrase()
    except IndexError as e:
        print u'用法1 训练: python invoker.py -train'
        print u'用法2 查询: python invoker.py -query'
        print u'用法3 批量查询: python invoker.py -query_in_batch'
#         print u'用法4 生成短语: python invoker.py -phrase'

from gensim.models.keyedvectors import KeyedVectors

def main_(input_file, word_list_file_list):

#     term_set = set()
#     f = file('TCMSem.txt')
#     for line in f:
#         line = line.decode('utf8').strip()
#         term_list = line.split()
#         if term_list[0] not in term_set:
#             term_set.add(term_list[0])
#     f.close()
    
    print u'正在加载模型......'
#     word_vectors = KeyedVectors.load_word2vec_format('700_token_glove_norm.txt', binary=False)  # C text format
    word_vectors = KeyedVectors.load_word2vec_format(input_file, binary=False)  # C text format
    
    print u'模型加载完毕'
    
    for word_list_file in word_list_file_list:
        try:
            f = file(word_list_file)
            lines = f.readlines()
            p, s, r = word_vectors.evaluate_word_pairs(word_list_file)
            # (pearson, spearman, ratio of pairs with unknown words)
            print input_file + '\t' + word_list_file + '\t' + str(len(lines)) + '\t' + str(p) + '\t' + str(s) + '\t' + str(r)
        except Exception as e:
            print e
            print word_list_file
            sys.exit()

#     f700 = file(output_file, 'w')
#     term_list = sorted(term_set)
#     for term in term_list:
#         try:
#             for item in word_vectors.most_similar(term, topn=100):
#                 f.write(term.encode('utf8') + '\t' + item[0].encode('utf8') + '\t' + str(item[1]) + '\n')
#         except:
#             continue
#     f.close()
    
def serialize(value, delimiter='\t', key_list=list()):
    if isinstance(value, list):
        str_list = list()
        for item in value:
            str_list.append(serialize(item))
        return delimiter.join(str_list)

    if isinstance(value, dict):
        str_list = list()
        for key in key_list:
            if key in value:
                str_list.append(serialize(value[key]))
            else:
                str_list.append('')
        return delimiter.join(str_list)
    
    # unicode or str
    if isinstance(value, basestring):
        return value.encode('utf8')

    return str(value)

def main__():
    # 合并第三人标注
    third_dict = dict()
    f_3rd = file('3rd.txt')
    for line in f_3rd:
        line = line.decode('utf8').strip()
        item_list = line.split()
        third_dict[(item_list[0], item_list[1])] = item_list[2]         
    f_3rd.close()

    word_dict = dict()
    f_wordlist = file('wordlist.txt')   
    for line in f_wordlist:
        line = line.decode('utf8').strip()
#         print line
        item_list = line.split()
        new_list = [item_list[0], item_list[1]]
        if (item_list[0], item_list[1]) in third_dict:
            new_list.append(round(float(int(third_dict[(item_list[0], item_list[1])]) + int(item_list[2]) + int(item_list[3])) / 3, 2))
            new_list.append(item_list[2])
            new_list.append(item_list[3])
            new_list.append(third_dict[(item_list[0], item_list[1])])
            print serialize(new_list)
        else:
            print item_list[0] + '\t' + item_list[1]
    f_wordlist.close() 
    
#     for key, value in word_dict.values():
#         print key[0] + '\t' + key[1] + '\t' + value + '\n'
    
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)
    
#     main__()

#     main()

#     # glove    
#     main_('/Users/qinanhu/Documents/tcm/zhu/publication/sci/glove/formula_token_glove_w5_64.txt')
#     main_('/Users/qinanhu/Documents/tcm/zhu/publication/sci/glove/formula_token_glove_w5_128.txt')
#     main_('/Users/qinanhu/Documents/tcm/zhu/publication/sci/glove/formula_token_glove_w10_64.txt')
#     main_('/Users/qinanhu/Documents/tcm/zhu/publication/sci/glove/formula_token_glove_w10_128.txt')
#      
#     main_('/Users/qinanhu/Documents/tcm/zhu/publication/sci/glove/700_token_glove_w5_64.txt')
#     main_('/Users/qinanhu/Documents/tcm/zhu/publication/sci/glove/700_token_glove_w5_128.txt')
#     main_('/Users/qinanhu/Documents/tcm/zhu/publication/sci/glove/700_token_glove_w10_64.txt')
#     main_('/Users/qinanhu/Documents/tcm/zhu/publication/sci/glove/700_token_glove_w10_128.txt')

#     # word2vec
#     main_('~/app/sourceCode/w2v/trunk/data/formula_token_w2v_cbow_w5_64.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/formula_token_w2v_cbow_w5_128.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/formula_token_w2v_cbow_w10_64.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/formula_token_w2v_cbow_w10_128.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/formula_token_w2v_skipgram_w5_64.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/formula_token_w2v_skipgram_w5_128.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/formula_token_w2v_skipgram_w10_64.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/formula_token_w2v_skipgram_w10_128.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/formula_token_w2v_skipgram_n5_w5_64.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/formula_token_w2v_skipgram_n5_w5_128.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/formula_token_w2v_skipgram_n5_w10_64.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/formula_token_w2v_skipgram_n5_w10_128.txt')
#  
#     main_('~/app/sourceCode/w2v/trunk/data/700_token_w2v_cbow_w5_64.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/700_token_w2v_cbow_w5_128.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/700_token_w2v_cbow_w10_64.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/700_token_w2v_cbow_w10_128.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/700_token_w2v_skipgram_w5_64.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/700_token_w2v_skipgram_w5_128.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/700_token_w2v_skipgram_w10_64.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/700_token_w2v_skipgram_w10_128.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/700_token_w2v_skipgram_n5_w5_64.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/700_token_w2v_skipgram_n5_w5_128.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/700_token_w2v_skipgram_n5_w10_64.txt')
#     main_('~/app/sourceCode/w2v/trunk/data/700_token_w2v_skipgram_n5_w10_128.txt')

#     group_by_frequency()

#     file_list = list()
#     entity_type_set = group_by_entity_type()
#     for entity_type in entity_type_set:
#         file_list.append('entity_type/TCMSem_' + entity_type + '.txt')
#     main_('/Users/qinanhu/Documents/tcm/zhu/publication/sci/w2v/700_token_w2v_skipgram_n5_w10_128.txt', file_list)
    
    file_list = list()
    relation_type_set = group_by_relation_type()
    for relation_type in relation_type_set:
        file_list.append('relation_type/TCMSem_' + relation_type + '.txt')
    main_('/Users/qinanhu/Documents/tcm/zhu/publication/sci/w2v/700_token_w2v_skipgram_n5_w10_128.txt', file_list)
