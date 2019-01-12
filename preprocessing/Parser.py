#!/usr/bin/env python
import sys
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import PorterStemmer
import xml.etree.cElementTree as ET
import re
import os
import numpy as np

class Parser:

    def __init__(self):
        """Initial the value
        """

        self.default_path = "./data/"
        self.keyword_list = []
        self.article_list = []
        self.art2key_dict = {}

    def XmlParser(self, path):
        tree = ET.ElementTree(file=path)
        count = 0
        book_count = 0

        #print("----------PubmedArticle----------")
        for md in tree.iter(tag='PubmedArticle'):
            if md.find('MedlineCitation').find('KeywordList') is not None:
                key4art_list = []
                count += 1
                #print("---------")
                #print(count, md.find('MedlineCitation').find('PMID').text)
                art_id = md.find('MedlineCitation').find('PMID').text
                if art_id not in self.article_list:
                    self.article_list.append(md.find('MedlineCitation').find('PMID').text)
                for key in md.find('MedlineCitation').find('KeywordList').findall('Keyword'):
                    if key.text is None:
                        continue
                    keys = key.text.split()
                    for k in keys:
                        if k is None:
                            continue
                        lower_key = k.lower()
                        #print(lower_key)
                        re_key = re.sub(r'[\W_]+', ' ', lower_key)
                        re_key = PorterStemmer().stem(re_key)
                        re_key_list = re_key.split()
                        #print("r", re_key_list)
                        for r in re_key_list:
                            key4art_list.append(r)#for specific article
                            
                            if r not in self.keyword_list and len(r)>1: 
                                self.keyword_list.append(r)#for total keyword table
                                
                self.art2key_dict[art_id] = key4art_list

        return sorted(self.article_list), sorted(self.keyword_list), self.art2key_dict
    
    def datalist(self, path):
        file_list = []
        for f in os.listdir(path):
            fname, ftype = os.path.splitext(f)
            if ftype == ".xml":
                file_list +=[path+f]
        return file_list
    
    def dict2arr(self, art2key_dict, keyword_list):
        keyword_len = len(keyword_list)
        article_len = len(art2key_dict)
        row = [] 
        col = []
        dictkey_list = sorted(list(art2key_dict.keys()))
        dictval_list = sorted(list(art2key_dict.values()))
        
        for i in range(article_len):
            col =[]
            for j in range(keyword_len):
                if keyword_list[j] in dictval_list[i]:
                    col.append(1)
                else:
                    col.append(0)
            row.append(col)
        
        return row

    def savelist(self, data_list, filename):
        f = open("./processed/"+filename+".txt", "w+")
        for i in range(len(data_list)):
            f.write(str(i)+" "+str(data_list[i])+"\n")
        f.close()

    def savedict(self, data_dict, filename):
        f = open("./processed/"+filename+".txt", "w+")
        for key, values in data_dict.items():
            txt = str(key)
            for v in values:
                txt += " "+str(v)
            f.write(txt+"\n")
        f.close()

if __name__ == '__main__':
    path = "./data/"
    parser = Parser()
    keyword_list = []
    article_list = []
    art2key_dict = {}
    file_list = parser.datalist(path)

    print("Total file :", file_list)
    for file_path in file_list:
        article_list, keyword_list, art2key_dict = parser.XmlParser(file_path)

    art2key_arr = np.array(parser.dict2arr(art2key_dict, keyword_list))
    print("Total article num : ", len(article_list))
    print("Total keyword num : ", len(keyword_list))
    
    parser.savelist(keyword_list, "keywordTable")
    parser.savelist(article_list, "articleTable")
    parser.savedict(art2key_dict, "art2keyTable")
    np.save("./processed/art2key.npy", art2key_arr)

