# -*- coding: utf-8 -*-
"""Untitled56.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aCn-dAMP2zpfjFRA2b_Ts5G58rJVbWKr
"""

from bs4 import BeautifulSoup
from keybert import KeyBERT
from multi_rake import Rake
from summa import keywords
import yake
from gensim.summarization import keywords
from IPython.display import HTML
import pandas as pd
import requests
import os
import argparse
import spacy
nlp = spacy.load("en_core_web_lg")


class keyword_extraction():
  def __init__(self,html_path, saving_path, method):
    self.html_path = html_path
    self.saving_path = saving_path
    self.method = method
    self.text = ''
    self.span_list = []

  def extract_span_list(self):
    with open(self.html_path, 'r') as f:
      html = f.read()
      soup = BeautifulSoup(html, features="html.parser")
      with open('/content/html_ex.html','w', encoding="utf-8")as file:
       file.write(soup.prettify())
      # kill all script and style elements
     
      soup_elem = soup.find_all("span")
      for span_elem in soup_elem:
        #print(span_elem)
        span_elem.extract() 
        span_text = span_elem.get_text().strip()
        lines = (line.strip() for line in span_text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  ") if len(phrase.strip())>9 )
        # drop blank lines
        #text_write = '\n'.join(chunk for chunk in chunks if chunk)
        span_text = ' '.join(chunk for chunk in chunks if chunk)
        if len(span_text)>9 and 'http' not in span_text and 'doi' not in span_text and 'Chapter' not in span_text:
          # print(span_text)
          # print('-'*50)
          self.span_list.append(span_text)
    return self.span_list      
  #def tf_idf(self):
  
  def clean(self,df):
      def tagger(x):
         return nlp(x)[0].pos_

      def lemma(x):
        #print(nlp(x)[0].lemma_)  
        return nlp(x)[0].lemma_ 
      
      df['POS']= df['keyword/phrase'].apply(lambda x: tagger(x))
      df['Lemma']= df['keyword/phrase'].apply(lambda x: lemma(x))
      df= df[df['keyword/phrase'] == df['Lemma'] ]
      df= df[df.POS.isin(['NOUN', 'PROPN', 'ADJ', 'ADV'])]
      df= df[~df['keyword/phrase'].apply(lambda x: lemma(x)).isin(['http','https', 'publication','Chapter'])]
      df = df.drop(columns = ['Lemma'], axis = 0)
      return df


  def extract_text_fom_html(self):

    with open(self.html_path, 'r') as f:
      html = f.read()
      soup = BeautifulSoup(html, features="html.parser")
     
      for script in soup(["script", "style"]):
          script.extract()    # rip it out
      
      # get text
      text = soup.get_text()
      #print(text)
      # break into lines and remove leading and trailing space on each
      lines = (line.strip() for line in text.splitlines())
      # break multi-headlines into a line each
      chunks = (phrase.strip() for line in lines for phrase in line.split("      ") if len(phrase.strip())>9 )
      # drop blank lines
      #text_write = '\n'.join(chunk for chunk in chunks if chunk)
      text = '\n '.join(chunk for chunk in chunks if chunk)
      self.text = text
      #print(text)
      # TEXT_ = f'Chapter06_text.txt'
      # saving_path = '/content/'     
      with open('text.txt', 'w') as file:
          file.write(text)
      return self.text
  def extract_keywords_rake(self):
    rake = Rake()
    self.extract_text_fom_html()
    keywords_Rake = rake.apply(self.text)
    df_Rake =pd.DataFrame(keywords_Rake)
    df_Rake.rename(columns = {0:'keyword/phrase',1:'score'}, inplace = True)
    df_Rake = self.clean(df_Rake)
    df_Rake.to_csv(self.saving_path +'Rake_keywords.csv',index=None)

  def extract_keywords_gensim(self):
    self.extract_text_fom_html()
    keywords_gensim= keywords(self.text,words = 100,scores = True, pos_filter =('NN','ADJ'),lemmatize = False, deacc =False) # run over all parameters 
    df_gensim =pd.DataFrame(keywords_gensim)
    df_gensim.rename(columns = {0:'keyword/phrase',1:'score'}, inplace = True)
    df_gensim = self.clean(df_gensim)
    df_gensim.to_csv(self.saving_path +'gensim_keywords.csv',index=None)  

  def extract_keywords_yake(self):
    self.extract_text_fom_html()
    kw_extractor = yake.KeywordExtractor(top=100, stopwords=None)
    keywords_yake = kw_extractor.extract_keywords(self.text)
    df_yake =pd.DataFrame(keywords_yake)
    df_yake.rename(columns = {0:'keyword/phrase',1:'score'}, inplace = True)
    df_yake = self.clean(df_yake)
    df_yake.to_csv(self.saving_path +'yake_keywords.csv',index=None) 
    # for kw, v in keywords_yake:
    #   print("Keyphrase: ",kw, ": score", v)  

  def extract_keywords_textrank(self):
    self.extract_text_fom_html()
    keywords_textrank = keywords.keywords(self.text, scores=True)
    df_textrank = pd.DataFrame(keywords_textrank)
    df_textrank.rename(columns = {0:'keyword/phrase',1:'score'}, inplace = True)
    df_textrank = self.clean(df_textrank)
    df_textrank.to_csv(self.saving_path +'textrank_keywords.csv',index=None)    

  def extract_keywords_keyBERT(self):
    kw_model = KeyBERT(model='all-mpnet-base-v2')
    keywords_keyBERT = kw_model.extract_keywords(self.text, 
                                     keyphrase_ngram_range=(1, 2), 
                                     stop_words='english', 
                                     highlight=True,
                                     top_n=10)  
    
  def main(self):
    if method == 'rake':
      self.extract_keywords_rake()
    elif method == 'yake':  
      self.extract_keywords_yake()
    elif method == 'gensim':  
      self.extract_keywords_gensim()
    elif method == 'textrank':  
      self.extract_keywords_textrank() 
    elif method == 'keyBERT':  
      self.extract_keywords_keyBERT() 


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--html_path',
                      required=True,
                      help='give the path where your html lives: /...')
    parser.add_argument('--saving_path',
                      required=True,
                      help='path of the folder where you want to save the files : /...'
                      )
    parser.add_argument('--method',
                      required=True,  choices=['rake','yake','gensim','keyBERT','textrank'],
                      help='which method you want to us to extact keywords /...')
    

    args = parser.parse_args()

    html_path = args.html_path #'/content/semanticClimate/ipcc/ar6/wg3/Chapter06/fulltext.flow.html'
    saving_path = args.saving_path  #'/content/'
    method = args.method
    
    keyword_extractions = keyword_extraction(html_path,saving_path,method)
    keyword_extractions.main()
