#!python2

# NLP Project Part 2
# Description: derives semantic representation from parse tree in sql query format and returns answer from DB
# Authors: Shaika Chowdhury and Surbhi Arora
# Date: April-May 2016


from __future__ import division
import nltk, re, pprint
from nltk.tokenize import RegexpTokenizer
from stat_parser import Parser

import unicodedata
import sys
import string
import json
import collections
import re
import nltk.classify.util, nltk.metrics
import pickle
import math, itertools
import os
from nltk.stem.porter import *
import sqlite3
import sys

currentQuery = "";
sqlQuery = None;


mu_vf_list = []
mu_nf_list = []
mo_vf_list = []
mo_nf_list = []
geo_vf_list=[]
geo_nf_list=[]
geo_pp_list = []
amb_list=[]

PropNoun_list=[]

SELECT=" select "
FROM=" from "
WHERE=" where "

special_word_noun=[]
special_word_verb=[]
special_word_adj=[]
special_word_prep=[]
tagname = ".label()"
year=None
flag_wh = False
flag_when = False


pob_dict={"American":"USA","British":"UK","German":"Germany","Italian":"Italy","French":"France"};

##---------------------------------------------##
##Parse Tree Traversal-------------------------##
##---------------------------------------------##
def parseSentences(sentence):

    parser = Parser()
    sentence=sentence.encode('utf-8')
##    print parser.parse(sentence),"\n\n"
    
    return parser.parse(sentence)
##----------------------------------------------------------------------------------------------##
##method for traversing the parse tree for movie sentences and calling semantic attachments methods
##----------------------------------------------------------------------------------------------##
def GrammarRulesAndSemAttach(par):
    global SELECT
    s=par.label()+"--->"
    global special_word_noun
    global special_word_verb
    global special_word_adj
    global special_word_prep
    global year
    global flag_wh
    global flag_when

    FINALSEM=None
##    year=None
    flag_last=False
    flag_when = False
#--- If question is of by WH type by default Select is set as P.name it will be replaced after 
    if par[0].label()=="WHNP" or par[0].label()=="WHADVP":
        SELECT+=" P.NAME"
##        print par[0][0].label()
        flag_last =True
        flag_wh = True
    elif par[0].label()=='SQ' or par[0].label()=='VBZ' or par[0].label()=='VBD'or  par[0].label()=='VP':
        SELECT+=" count(*) "
        flag_last=True
        flag_wh = False
        flag_when = False


##    if par.label()=='SBARQ' or par.label()=='VP+SQ' or par.label()=='SQ+VP+VP':
##        SELECT+=" count(*) "
##        flag_last=True

    for i in range(len(par)):
        flag=False
        flag2=False
        s=s+par[i].label()+" "
        for j in par[i]:
            
            if (isinstance(j[0],str)):
                if (isinstance(j,str)):
                    ##--- Check for movie name with "-"
                    if j.find('-') != -1: 
                        pn=ProperNoun()
                        PropNoun_list.append(j)
                        '''
                        l1= j.split('-')
                        pn=ProperNoun()
                        for x in l1 :
                            PropNoun_list.append(pn.sem(x))
                        '''
##                    print par[i].label(),"---->", j
##                    if par[i].label()=='NN' or par[i].label()=='NNS' or par[i].label()=='NNP' or par[i].label()=='NNPS':
                    if par[i].label()=='NNP' or par[i].label()=='NNPS'or par[i].label()=='NNS' :
                        pn=ProperNoun()
                        PropNoun_list.append(pn.sem(j))
                    if par[i].label()=='NN' or par[i].label()=='NNS' :
                        special_word_noun.append(j)
                         
                        l = re.findall('[A-Z][a-z]+[^A-Z]*',j)
                        if (len(l) != 0):
                            pn=ProperNoun()
    ##                        pn.sem(j)
                            PropNoun_list.append(pn.sem(j))

                    if par[i].label()=='JJS' or par[i].label()=='JJ':
                         special_word_adj.append(j)
                    if par[i].label()=='CD':
                        if len(j) == 4 :
                            year=j
                        else:
                             pn=ProperNoun()
                             PropNoun_list.append(pn.sem(j))
                    if par[i].label()=='IN':
##                        special_word_prep=j
                        special_word_prep.append(j)
                    if par[i].label()=='VBZ' or par[i].label()=='VBD' or par[i].label()=='VBN' or par[i].label()=='VB' or par[i].label()=='VBP' or par[i].label()=='VBG':
                        special_word_verb.append(j)
                else:
                    if j[0].find('-') != -1: 
                        pn=ProperNoun()
                        PropNoun_list.append(j[0])
                        '''                            
                        l1= j[0].split('-')
                        pn=ProperNoun()
                        for x in l1 :
                        
                            PropNoun_list.append(pn.sem(x))
                        '''
##                    if j.label()=='NN' or j.label()=='NNS' or j.label()=='NNP' or j.label()=='NNPS':
                    if j.label()=='NNP' or j.label()=='NNPS'or j.label()=='NNS' :
##                    if par[i].label()=='NN' or par[i].label()=='NNS' :
                        pn=ProperNoun()
##                            pn.sem(j)
##                        print 'j1'," ",j
##                        print 'par[i].label()'," ",par[i].label()
                        PropNoun_list.append(pn.sem(j[0]))
##                        PropNoun_list.add(pn.sem(j[0]))
##                        print 'j2[0]'," ",j[0]
##                        print 'prop list'," ",PropNoun_list
##                        special_word_noun=j[0]
                    if j.label()=='NN' or j.label()=='NNS' :
##                        special_word_noun=j[0]
                        special_word_noun.append(j[0])
                        l = re.findall('[A-Z][a-z]+[^A-Z]*',j[0])
                        if (len(l) != 0):
                             pn=ProperNoun()
                             PropNoun_list.append(pn.sem(j[0]))

                    if j.label()=='JJS' or par[i].label()=='JJ':
                        if j[0].find('-') == -1: 
                            special_word_adj.append(j[0])
                        else:
                            l1= j[0].split('-')
                            prop =" ".join(str(x) for x in l1)
                            pn=ProperNoun()
                            PropNoun_list.append(pn.sem(prop))
                            

                    if j.label()=='CD':
                        if len(j[0]) == 4 :
                            year=j[0]
                        else:
                             pn=ProperNoun()
                             PropNoun_list.append(pn.sem(j))

                    if j.label()=='IN':
                            special_word_prep.append(j[0])

                    if j.label()=='VBZ' or j.label()=='VBD' or j.label()=='VBN' or j.label()=='VB' or j.label()=='VBP' or j.label()=='VBG':
                            special_word_verb.append(j[0])

                    if j.label()=='WRB':
                        #print "Fla when"
                        flag_when = True
                    if(flag==False):
                        s2=par[i].label()+"---->"
                        flag=True
##                        if par[i].label()=='NN' or par[i].label()=='NNS' or par[i].label()=='NNP' or par[i].label()=='NNPS':
                        if par[i].label()=='NNP' or par[i].label()=='NNPS'or par[i].label()=='NNS' or par[i].label()=='NN':
##                        if par[i].label()=='NN' or par[i].label()=='NNS' :
                            pn=ProperNoun()
                            PropNoun_list.append(pn.sem(j))
                            PropNoun_list.append(pn.sem(j[0]))
                        if par[i].label()=='NN' or par[i].label()=='NNS' :
                            special_word_noun=j
                        if par[i].label()=='JJS' or par[i].label()=='JJ':
                            special_word_adj.append(j)
                        if par[i].label()=='CD':
                            year=j
                        if par[i].label()=='IN':
                            special_word_prep.append(j)
                        if par[i].label()=='VBZ' or par[i].label()=='VBD' or par[i].label()=='VBN' or par[i].label()=='VB' or par[i].label()=='VBP' or par[i].label()=='VBG':
                            special_word_verb.append(j)



##                        if par[i].label()=='SBARQ' or par[i].label()=='VP+SQ' or par[i].label()=='SQ+VP+VP':
##                            SELECT+=" count(*) "

                    
                    s2=s2+j.label()+" "
                    flag2=True
            else:
                if(flag==False):
##                    print 'j 5.label()'," ",j.label()
                    s2=par[i].label()+"---->"
                    flag=True
                    s2=s2+j.label()+" "
##                    if par[i].label()=='SBARQ' or par[i].label()=='VP+SQ' or par[i].label()=='SQ+VP+VP':
##                        SELECT+=" count(*)"

                elif(flag==True):
                    s2=s2+j.label()+" "

                GrammarRulesAndSemAttach(j)

##        if(flag2==True):

##            print s2
##
##    print s

##    vb=Verb()
##    FROM1,WHERE1=vb.sem(PropNoun_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year)
##    print "from"," ",FROM1,"WHERE"," ",WHERE1
    if flag_last==True:
        if flag_wh == False:
            vb=Verb()
            FROM1,WHERE1=vb.sem(PropNoun_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year)
        elif flag_wh == True:
            vb=Verb()
            FROM1,WHERE1=vb.sem_wh(PropNoun_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year)


##        FINALSEM = "select" + " " + SELECT + FROM + "where" + WHERE;
##### ------- (SQL QUERY CREATION)
        FINALSEM = SELECT + FROM + WHERE;

##        print FINALSEM

    return FINALSEM
    

####-----------------------------------------------------------------------------------------------------------########
####Does semantic attachments of verb for movies sentences and implemneting lambda function a sto set the where clause
####-----------------------------------------------------------------------------------------------------------########

class Verb:

    def sem(self,prop_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year):
        global FROM
        global WHERE
##        if 'actor' in special_word_noun:
##            print 'yes actor'
        
##        FROM=""
##        WHERE=""
        check=[]
        flag_start=False
        flag_start2=False
        flag_start3=False
        flag0=False
        flag00=False
        flag1=False
        flag2=False
        flag3=False
        flag3_0=False
        flag4=False
        flag4_1=False
        flag_mov=False
        flag_mov1=False
        flag_mov2=False
        flag_mov3=False
        flag_mov4=False
        flag_mov5=False
        flag_mov6=False
        temp=None
        if 'DiCaprio' in special_word_adj:
            special_word_adj.remove('DiCaprio');
            prop_list.append('DiCaprio')
        elif 'DiCaprio' in special_word_verb:
            special_word_verb.remove('DiCaprio');
            prop_list.append('DiCaprio')
        elif 'DiCaprio' in special_word_prep:
            special_word_prep.remove('DiCaprio');
            prop_list.append('DiCaprio')
        if 'De' in special_word_adj:
            special_word_adj.remove('De');
            prop_list.append('De')
        elif 'De' in special_word_verb:
            special_word_verb.remove('De');
            prop_list.append('De')
        elif 'De' in special_word_prep:
            special_word_prep.remove('De');
            prop_list.append('De')

##        print "old prop list"," ",prop_list

##        print " old prop list"," ",prop_list
        regex = re.compile(r'^-?[0-9]+$')
        for i  in range(len(prop_list)):
            if regex.match(prop_list[i]):
                part=prop_list[i]
##                print "part"," ",part
                if (QueryMovieDB(prop_list[i-1]))==0:
                    part2=prop_list[i-1]+part
##                    print "part 2"," ",part2
                    prop_list.remove(prop_list[i-1]);
                    prop_list.remove(part);
                    prop_list.append(part2)
                
        for prop in prop_list:
            check=QueryMovieDB(prop)
            if check==0 and 'by' in special_word_prep and len(prop_list)==2:
                temp=prop
                flag00=True
            elif flag00==True and check==1:                
                FROM+=' director D INNER JOIN Person P ON D.director_id = P.id '
                FROM+=' INNER JOIN Movie M ON D.movie_id=M.id '
                strr= "P.name like '%"+prop+"%'"
                WHERE+=strr
                strr="and M.name like '%"+temp+"%'"
                WHERE+=strr
            elif ('Age' in prop_list or 'Ice' in prop_list) and flag_start3==False and (check==1 or check==0) and 'by' in special_word_prep and len(prop_list)>2:
                temp=prop
                flag_mov5=True
                flag_start3=True
            elif flag_mov5==True and not (prop=='Age' or prop=='Ice') and check==1:                
                FROM+=' director D INNER JOIN Person P ON D.director_id = P.id '
                FROM+=' INNER JOIN Movie M ON D.movie_id=M.id '
                strr= "P.name like '%"+prop+"%'"
                WHERE+=strr
                strr="and M.name like '%"+temp+"%'"
                WHERE+=strr
                flag_mov5=False

            elif flag_start==False and check==0 and 'by' in special_word_prep and len(prop_list)>2 and not ('Age' in prop_list or 'Ice' in prop_list):
                temp=prop
                flag_mov=True
                flag_start=True

            elif flag_mov==True and check==1:                
                FROM+=' director D INNER JOIN Person P ON D.director_id = P.id '
                FROM+=' INNER JOIN Movie M ON D.movie_id=M.id '
                strr= "P.name like '%"+prop+"%'"
                WHERE+=strr
                strr="and M.name like '%"+temp+"%'"
                WHERE+=strr
                flag_mov=False
            elif check==1 and ('direct' in special_word_adj or 'direct' in special_word_verb) and len(prop_list)==2:
                FROM+=' director D INNER JOIN Person P ON D.director_id = P.id '
                FROM+=' INNER JOIN Movie M ON D.movie_id=M.id '
                strr= "P.name like '%"+prop+"%'"
                WHERE+=strr
                flag_mov3=True
            elif flag_mov3==True and check==0:                
                strr="and M.name like '%"+prop+"%'"
                WHERE+=strr
                flag_mov3==False
            elif flag_start2==False and check==1 and  ('direct' in special_word_adj or 'direct' in special_word_verb) and len(prop_list)>2:
                FROM+=' director D INNER JOIN Person P ON D.director_id = P.id '
                FROM+=' INNER JOIN Movie M ON D.movie_id=M.id '
                strr= "P.name like '%"+prop+"%'"
                WHERE+=strr
                flag_mov4=True
                flag_start2=True
            elif flag_mov4==True and check==0:                
                strr="and M.name like '%"+prop+"%'"
                WHERE+=strr
                flag_mov4=False
            elif check==1 and ('director' in special_word_noun or 'actor' in special_word_noun) and len(prop_list)==1 and 'is' in special_word_verb :
                if 'director' in special_word_noun:
                    FROM+=' director D INNER JOIN Person P ON D.director_id = P.id '
                elif 'actor' in special_word_noun:
                    FROM+=' actor D INNER JOIN Person P ON D.actor_id = P.id '
                    strr= "P.name like '%"+prop+"%'"
                    WHERE+=strr
            elif  check==1 and 'born' in special_word_verb and year is None:
                FROM+=' person '
##                strr= ' name like \' %s \' ' % prop
                strr= "name like '%"+prop+"%'"
                WHERE+=strr

                flag2=True
            elif  flag2==True and check==2 :
                strr="and pob like '%"+prop+"%'"
                WHERE+=strr
            elif  check==1 and 'born' in special_word_verb and year is not None:
                FROM+=' person '
                strr= "name like '%"+prop+"%'"
                WHERE+=strr
                strr="and dob like '%"+year+"%'"
                WHERE+=strr
            elif check==1 and ('star' in special_word_noun or 'act' in special_word_noun):
                FROM+=' Person P  INNER JOIN Actor A ON P.id = A.actor_id '
                strr= "P.name like '%"+prop+"%'"
                WHERE+=strr
                flag4=True
            elif flag4==True and check==0:
                FROM+=' INNER JOIN Movie M ON A.movie_id = M.id '
                strr="and M.name like '%"+prop+"%'"
                WHERE+=strr
                flag4=False
            elif check==1 and ('oscar' in special_word_noun or 'best' in special_word_adj)  and year is not None and flag_mov6==False:
                check3=QueryMovieDB(year)
                if check3==3:
                    FROM+=' Person P  INNER JOIN Oscar O ON P.id = O.person_id '
                    strr= "P.name like '%"+prop+"%'"
                    WHERE+=strr
                    strr= "and O.year = "+year+" "
                    WHERE+=strr
                    if 'actor' in special_word_noun:
                        tmp4='BEST-ACTOR'
                        strr="and O.type like '%"+tmp4+"%'"
                        WHERE+=strr
                    if 'actress' in special_word_noun:
                        tmp4='BEST-ACTRESS'
                        strr="and O.type like '%"+tmp4+"%'"
                        WHERE+=strr
                    if 'director' in special_word_noun:
                        tmp4='BEST-DIRECTOR'
                        strr="and O.type like '%"+tmp4+"%'"
                        WHERE+=strr

                    flag_mov6=True
            elif ("American" in special_word_adj or  "Italian" in special_word_adj or "French" in special_word_adj or "British" in special_word_adj or "German" in special_word_adj) and ('oscar' in special_word_noun or 'win' in special_word_verb ):
                if "American" in special_word_adj:
                    tmp_adj="American"
                    tmp3=pob_dict.get(tmp_adj)
                elif "Italian" in special_word_adj:
                    tmp_adj="Italian"
                    tmp3=pob_dict.get(tmp_adj)
                elif "French" in special_word_adj:
                    tmp_adj="French"
                    tmp3=pob_dict.get(tmp_adj)
                elif "British" in special_word_adj:
                    tmp_adj="British"
                    tmp3=pob_dict.get(tmp_adj)
                elif "German" in special_word_adj:
                    tmp_adj="German"
                    tmp3=pob_dict.get(tmp_adj)
                if ('actor' in special_word_noun or 'actress' in special_word_noun or 'director' in special_word_noun) and year is not None:
                    if 'actor' in special_word_noun:
                        tmp4='actor'
                    elif 'actress' in special_word_noun:
                        tmp4='actress'
                    elif 'director' in special_word_noun:
                        tmp4='director'

                    FROM+=' Person P  INNER JOIN Oscar O ON P.id = O.person_id '
                    strr= "O.year = "+year+" "
                    
                    WHERE+=strr
                    strr= "and P.pob like '%"+tmp3+"%'"
                    WHERE+=strr
                    strr= "and O.type like '%"+tmp4+"%'"
                    WHERE+=strr
            elif check==1 and ('win' in special_word_verb or 'get' in special_word_verb or 'oscar' in special_word_noun) and 'best' in special_word_adj and 'movie' in special_word_noun and ('film' in special_word_noun or 'picture' in special_word_noun):
                tmp4='BEST-PICTURE'
                FROM+=' Oscar O  INNER JOIN Actor A ON A.movie_id = O.movie_id  INNER JOIN Person P ON A.actor_id = P.id '
                strr= "P.name like '%"+prop+"%'"
                WHERE+=strr
                strr= "and O.type like '%"+tmp4+"%'"
                WHERE+=strr
            elif check==1 and ('win' in special_word_verb or 'get' in special_word_verb) and 'best' in special_word_adj and  not ('supporting' in special_word_verb):
                if 'actor' in special_word_noun:
                    FROM+=' Oscar O  INNER JOIN Person P ON P.id = O.person_id '
                    strr= "P.name like '%"+prop+"%'"
                    WHERE+=strr
                    strr= "and O.type like 'best-actor'"
                    WHERE+=strr
                elif 'actress' in special_word_noun:
                    FROM+=' Oscar O  INNER JOIN Person P ON P.id = O.person_id '
                    strr= "P.name like '%"+prop+"%'"
                    WHERE+=strr
                    strr= "and O.type like 'best-actress'"
                    WHERE+=strr
                elif 'director' in special_word_noun:
                    FROM+=' Oscar O  INNER JOIN Person P ON P.id = O.person_id '
                    strr= "P.name like '%"+prop+"%'"
                    WHERE+=strr
                    strr= "and O.type like 'best-director'"
                    WHERE+=strr
                    
            elif check==1 and 'supporting' in special_word_verb and 'best' in special_word_adj  and ('oscar' in special_word_noun or 'win' in special_word_verb ):
                if 'actress' in special_word_noun:
                    FROM+=' Oscar O  INNER JOIN Person P ON P.id = O.person_id '
                    strr= "P.name like '%"+prop+"%'"
                    WHERE+=strr
                    strr= "and O.type like 'best-supporting-actress'"
                    WHERE+=strr
                if 'actor' in special_word_noun:
                    FROM+=' Oscar O  INNER JOIN Person P ON P.id = O.person_id '
                    strr= "P.name like '%"+prop+"%'"
                    WHERE+=strr
                    strr= "and O.type like 'best-supporting-actor'"
                    WHERE+=strr
                
            elif check==0 and ('win' in special_word_verb or special_word_verb=='get') and 'best' in special_word_adj and len(prop_list)==1:
                if ('movie' in special_word_noun or 'film' in special_word_noun or 'picture' in special_word_noun) and year is not None:
                    FROM+=' oscar O INNER JOIN Movie M ON O.movie_id = M.id '
                    strr="M.name like '%"+prop+"%'"
                    WHERE+=strr
                    tmp2='BEST-PICTURE'
                    strr= "and O.year = "+year+" "
                    WHERE+=strr
                    strr= "and O.type like '%"+tmp2+"%'"
                    WHERE+=strr
                elif 'movie' in special_word_noun or 'film' in special_word_noun or 'picture' in special_word_noun:
                    FROM+=' Oscar O  INNER JOIN Movie M ON M.id = O.movie_id '
                    strr= "M.name like '%"+prop+"%'"
                    WHERE+=strr
                    strr= "and O.type like 'best-picture'"
                    WHERE+=strr
                
            elif check==0 and 'best' in special_word_adj and len(prop_list)==1 and year is not None:
                FROM+=' oscar O INNER JOIN Movie M ON O.movie_id = M.id '
                strr="M.name like '%"+prop+"%'"
                WHERE+=strr
                tmp2='BEST-PICTURE'
                strr= "and O.year = "+year+" "
                WHERE+=strr
                strr= "and O.type like '%"+tmp2+"%'"
                WHERE+=strr
##
            elif check==0 and ('win' in special_word_verb or 'get' in special_word_verb) and 'best' in special_word_adj and len(prop_list)>1 and flag_mov1==False:
                if ('movie' in special_word_noun or'film' in special_word_noun or 'picture' in special_word_noun) and year is not None:
                    FROM+=' oscar O INNER JOIN Movie M ON O.movie_id = M.id '
                    strr="M.name like '%"+prop+"%'"
                    WHERE+=strr
                    tmp2='BEST-PICTURE'
                    strr= "and O.year = "+year+" "
                    WHERE+=strr
                    strr= "and O.type like '%"+tmp2+"%'"
                    WHERE+=strr
##                    print 'test 19_0'
                    flag_mov1=True


                elif 'movie' in special_word_noun or 'film' in special_word_noun or 'picture' in special_word_noun:
                    FROM+=' Oscar O  INNER JOIN Movie M ON M.id = O.movie_id '
                    strr= "M.name like '%"+prop+"%'"
                    WHERE+=strr
                    strr= "and O.type like 'best-picture'"
                    WHERE+=strr
                    flag_mov1=True
            elif check==0 and 'best' in special_word_adj and len(prop_list)>1 and year is not None and flag_mov2==False and not ('win' in special_word_verb or 'get' in special_word_verb):
                FROM+=' oscar O INNER JOIN Movie M ON O.movie_id = M.id '
                strr="M.name like '%"+prop+"%'"
                WHERE+=strr
                tmp2='BEST-PICTURE'
                strr= "and O.year = "+year+" "
                WHERE+=strr
                strr= "and O.type like '%"+tmp2+"%'"
                WHERE+=strr
                flag_mov2=True

            check=-1

        if not prop_list:
            if ("American" in special_word_adj or  "Italian" in special_word_adj or "French" in special_word_adj or "British" in special_word_adj or "German" in special_word_adj) and ('oscar' in special_word_noun or 'win' in special_word_verb ):
                if "American" in special_word_adj:
                    tmp_adj="American"
                    tmp3=pob_dict.get(tmp_adj)
                elif "Italian" in special_word_adj:
                    tmp_adj="Italian"
                    tmp3=pob_dict.get(tmp_adj)
                elif "French" in special_word_adj:
                    tmp_adj="French"
                    tmp3=pob_dict.get(tmp_adj)
                elif "British" in special_word_adj:
                    tmp_adj="British"
                    tmp3=pob_dict.get(tmp_adj)
                elif "German" in special_word_adj:
                    tmp_adj="German"
                    tmp3=pob_dict.get(tmp_adj)
                if ('actor' in special_word_noun or 'actress' in special_word_noun or 'director' in special_word_noun) and year is not None:
                    if 'actor' in special_word_noun:
                        tmp4='actor'
                    elif 'actress' in special_word_noun:
                        tmp4='actress'
                    elif 'director' in special_word_noun:
                        tmp4='director'

                    FROM+=' Person P  INNER JOIN Oscar O ON P.id = O.person_id '
                    strr= "O.year = "+year+" "
                    
                    WHERE+=strr
                    strr= "and P.pob like '%"+tmp3+"%'"
                    WHERE+=strr
                    strr= "and O.type like '%"+tmp4+"%'"
                    WHERE+=strr

        return FROM,WHERE


############################################################################################################################################

    def sem_wh(self,prop_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year):
        global FROM
        global WHERE
        global SELECT

##        FROM=""
##        WHERE=""
        check=[]
        flag_start=False
        flag0=False
        flag00=False
        flag1=False
        flag2=False
        flag3=False
        flag3_0=False
        flag4=False
        flag4_1=False
        temp=None
        global flag_when

        for prop in prop_list:
            check=QueryMovieDB(prop)
            if check==1 and 'by' in special_word_prep :
                FROM+=' director D INNER JOIN Person P ON D.director_id = P.id '
                strr=' P.name like \' %s \'  ' % prop
                WHERE+=strr
                flag_start==True
                flag0=True
##                print 'test1'
            if  "directed" in special_word_verb :
##                print "proper noun",prop
                if len(FROM)<10:
                    FROM+='  Person P INNER JOIN director D ON D.director_id = P.id '
                    flag_start=True
                    flag0=True
                    if  check==0:
                        FROM+=' INNER JOIN Movie M ON D.movie_id=M.id '
                if len(WHERE) ==7:
                    strr = "M.Name like '%"+prop+"%'"
                else:
                    strr="and M.Name like '%"+prop+"%'"
                WHERE+=strr

           
            elif flag00==True and check==1:                
                FROM+=' director D INNER JOIN Person P ON D.director_id = P.id '
                FROM+=' INNER JOIN Movie M ON D.movie_id=M.id '
                strr=' P.name like \' %s \'  ' % prop
                WHERE+=strr
                strr=' and M.name like \' %s \'  ' % temp
                WHERE+=strr
##                print 'test3'
            elif check==1 and 'director' in special_word_noun:
                FROM+=' director D INNER JOIN Person P ON D.director_id = P.id '
                strr=' P.name like \' %s \' ' % prop
                WHERE+=strr
                flag1=True
            elif flag1==True and check==0:
                FROM+=' INNER JOIN Movie M ON D.movie_id=M.id '
                strr=' and M.name like \' %s \'  ' % prop
                WHERE+=strr

            elif  check==1 and 'born' in special_word_verb:
                FROM+=' person '
                strr= ' name like \' %s \' ' % prop
                WHERE+=strr

##                WHERE+=" name like '%prop'"
                flag2=True
##                print 'test5'
            elif  flag2==True and check==2:
                strr=' and pob like \' %s \' ' % prop
                WHERE+=strr
            elif  check==0 and 'best' in special_word_adj and flag3_0==False:
                FROM+=' oscar O INNER JOIN Movie M ON O.movie_id = M.id '
                strr=' M.name  like \' %s \' ' % prop
                WHERE+=strr
                if year is not None and 'movie' in special_word_noun:
                    check2=QueryMovieDB(year)
                    if check2==3:
                        tmp2='BEST-PICTURE'
                        strr= ' and O.year  = \' %s \'  ' % year
                        WHERE+=strr
                        strr= ' and O.type like \' %s \' ' % tmp2
                        WHERE+=strr
            elif check==1 and 'star' in special_word_noun:
##                FROM+=' Person P  INNER JOIN Actor A ON P.id = A.actor_id '
                FROM+=' Person P  INNER JOIN Director D ON P.id = D.director_id '
                strr=' P.name like \' %s \'  ' % prop
                WHERE+=strr
                flag4=True
##                print 'test11'
            elif flag4==True and check==0:
                FROM+=' INNER JOIN Movie M ON D.movie_id = M.id '
                strr=' and M.name like \' %s \'  ' % prop
                WHERE+=strr
                flag4=False
##                print 'test12'
            elif check==1 and 'best' in special_word_adj:
##                FROM+=' Person P  INNER JOIN Actor A ON P.id = A.actor_id '
                #otype =
                if 'actor' in special_word_noun:
                    tmp6='actor'
                elif 'director' in special_word_noun:
                    tmp6='director'
                elif 'actress' in special_word_noun:
                    tmp6='actress'

                SELECT = "Select O.year"
                if len(FROM) <= 7:
                    FROM+=' Oscar O  INNER JOIN Person P ON P.id = O.person_id '
                if len(WHERE) ==7:
                    strr="P.name like '%"+prop+"%' and O.type like'BEST-"+tmp6+"'"
                else:
                    strr="and P.name like '%"+prop+"%'"
                WHERE+=strr
                flag4=True
##                print 'test when '

            check=-1
        if len(prop_list) ==0:
             
             if 'won' in special_word_verb or 'win' in special_word_verb:
                Otype = ""
                
                          
                if len(special_word_noun) ==1 :
                    
                    Otype = special_word_noun[0]
                else:
                    for i in special_word_noun:
                        if i != 'oscar':
                            Otype = i
                if flag_when == False: 
                    if Otype == 'movie' :
                        Otype = "PICTURE"
                        SELECT = "Select M.NAME"
                        FROM+=' Movie M INNER JOIN Oscar O ON M.id=O.movie_id '
                    else:
                        FROM+=' Person P INNER JOIN Oscar O ON P.id=O.person_id '
                    strr = "O.type like '%BEST-"+Otype+"%'"
                    WHERE+=strr
                    flag_start==True
                    flag0=True
    ##                print 'test13'
                    if year is not None:
                        WHERE +="AND O.YEAR LIKE '%"+year+"%'"
                elif flag_when ==True and 'win' in special_word_verb and len(special_word_adj) != 0:
                    pob = ""
                    if special_word_adj[0] in pob_dict.keys():
                        pob = pob_dict[special_word_adj[0]]
                     
                    SELECT = "Select O.year"
                    FROM+=' Oscar O  INNER JOIN Person P ON P.id = O.person_id '
                    strr="P.pob like '%"+pob+"%' and O.type like'BEST-"+Otype+"'"
                    WHERE+=strr
                    flag_when =False
             elif "directed" in special_word_verb:
                Otype = ""
##                print "direct check"
                
                if 'actor' in special_word_noun:
                    Otype='actor'
                elif 'director' in special_word_noun:
                    Otype='director'
                elif 'actress' in special_word_noun:
                    Otype='actress'
                elif 'movie' in special_word_noun:
                    Otype='movie'


##                Otype = special_word_noun
                if Otype=='movie':
                    Otype = "PICTURE"
                   
                FROM+=' Person P INNER JOIN DIRECTOR D ON P.id=D.director_id INNER JOIN Oscar O ON D.movie_id=O.movie_id '
                
                strr = "O.type like '%BEST-"+Otype+"%'"
                WHERE+=strr
##                print "direct test"
                if year is not None:
                    WHERE +="AND O.YEAR LIKE '%"+year+"%'"
            
             
             else:
                 FROM = ""
                 WHERE= ""
             check=-1
       
        return FROM,WHERE


####Does semantic attachments for Proper Nouns of all domains
class ProperNoun:
    
    def sem(self,prop):
        #print "prop",prop
        l = re.findall('[A-Z][a-z]+[^A-Z]*', prop)
        if (len(l) != 0):
            prop =" ".join(str(x) for x in l)
        seman_prop = prop
        #print "after",seman_prop
##        PropNoun_list.append(seman_prop)
##        return seman_prop
##        FROM+="HI"
        return seman_prop


##queries movie DB

def QueryMovieDB(str_check):


    check=0
    sqlite_file1 = 'oscar-movie_imdb.sqlite'        
    table_name1 = 'Person'   # name of the table to be queried
    attribute = 'name'
    table_name2 = 'Movie'   # name of the table to be queried
    conn1 = sqlite3.connect(sqlite_file1)
    cursor1 = conn1.cursor()
    attr_value1 = "%"+str_check                        

    cursor1.execute("select name from Person where name like :at ",{"at":attr_value1})
    exist1=cursor1.fetchall()
    cursor1.execute("select name from Movie where name like :at ",{"at":attr_value1})
    exist2=cursor1.fetchall()
    cursor1.execute("select pob from Person where pob like :at ",{"at":attr_value1})
    exist3=cursor1.fetchall()
    cursor1.execute("select year from Movie where year like :at ",{"at":attr_value1})
    exist4=cursor1.fetchall()
    cursor1.execute("select type from Oscar where type like :at ",{"at":attr_value1})
    exist5=cursor1.fetchall()
    cursor1.execute("select year from Oscar where year like :at ",{"at":attr_value1})
    exist6=cursor1.fetchall()
    cursor1.execute("select dob from Person where dob like :at ",{"at":attr_value1})
    exist7=cursor1.fetchall()




    
    number_of_rows1 =len(exist1)
    number_of_rows2 =len(exist2)
    number_of_rows3 =len(exist3)
    number_of_rows4 =len(exist4)
    number_of_rows5 =len(exist5)
    number_of_rows6 =len(exist6)
    number_of_rows7 =len(exist7)



    if number_of_rows1 > 0:
        check=1
    elif number_of_rows2 > 0:
        check=0
    elif number_of_rows3 > 0:
        check=2
    elif number_of_rows4 > 0:
        check=3
    elif number_of_rows5 > 0:
        check=4
    elif number_of_rows6 > 0:
        check=5
    elif number_of_rows7 > 0:
        check=6





    return check
        

##returns answer from DB of the new compositionally formed query (SQL QUERY CREATION)

def NewQuery(query):
##    print 'query'," ",query
##    check=0
    check =""
    try:
        sqlite_file_new = 'oscar-movie_imdb.sqlite'
        conn_new = sqlite3.connect(sqlite_file_new)
        cursor_new = conn_new.cursor()
        cursor_new.execute(query)
        exist_new=cursor_new.fetchall()
    ##    print 'exist_new'," ",exist_new
    ##    exist_new=cursor_new.fetchone()
        number_of_rows_new =len(exist_new)
    ##    print "number of rows",number_of_rows_new
            
        if number_of_rows_new > 0:
    
            if flag_wh ==True:
                check = exist_new[0][0]
    ##            print exist_new[0]
                if type(check)==int:
                    check=str(check)
    
    ##        else:
    ##            check=1
    
            elif flag_wh ==False:
                if exist_new[0][0] >0:
    ##        print 'exist_new[0]'," ",exist_new[0] 
                    check='yes'
                else:
                    check='no'
    #except (RuntimeError, TypeError, NameError):
    except Exception, e:
        pass
##    print 'check query'," ",check

    return check


##traverses the parse tree and calls semantic attachments method for geo sentences
def GrammarRulesAndSemAttach_geo(par):
    global SELECT

##    print 'prop list'," ",PropNoun_list
    s=par.label()+"--->"
##    SELECT=""
##    special_word_noun=None
##    special_word_verb=None
##    special_word_adj=None
##    special_word_prep=None
    global special_word_noun
    global special_word_verb
    global special_word_adj
    global special_word_prep
    global year
    global flag_wh
    global flag_when

    FINALSEM=None
##    year=None
    flag_last=False
    flag_when = False

##    print "qtype ",par[0].label()
    if par[0].label()=="WHNP" or par[0].label()=="WHADVP":
        SELECT+=" P.NAME"
##        print par[0][0].label()
        flag_last =True
        flag_wh = True
    elif par[0].label()=='SQ' or par[0].label()=='VBZ' or par[0].label()=='VBD'or  par[0].label()=='VP':
        SELECT+=" count(*) "
        flag_last=True
        flag_wh = False
        flag_when = False


##    if par.label()=='SBARQ' or par.label()=='VP+SQ' or par.label()=='SQ+VP+VP':
##        SELECT+=" count(*) "
##        flag_last=True

    for i in range(len(par)):
        flag=False
        flag2=False
        s=s+par[i].label()+" "
        for j in par[i]:
            
            if (isinstance(j[0],str)):
                if (isinstance(j,str)):
##                    print par[i].label(),"---->", j
##                    if par[i].label()=='NN' or par[i].label()=='NNS' or par[i].label()=='NNP' or par[i].label()=='NNPS':
                    if par[i].label()=='NNP' or par[i].label()=='NNPS'or par[i].label()=='NNS':

##                    if par[i].label()=='NN' or par[i].label()=='NNS' :

##                        print "NOUN"," ",j
##                        print 'j0'," ",j
##                        print 'par[i].label()'," ",par[i].label()
                        pn=ProperNoun()
##                        pn.sem(j)
                        PropNoun_list.append(pn.sem(j))
##                        PropNoun_list.add(pn.sem(j))
##                    if j.label()=='NN' or j.label()=='NNS' or j.label()=='NNP' or j.label()=='NNPS':
##                        print "NOUN"," ",j
##                        print 'j'," ",j
##                        print 'par[i].label()'," ",par[i].label()
##                        pn=ProperNoun()
####                        pn.sem(j)
##                        PropNoun_list.append(pn.sem(j[0]))

##                        PropNoun_list.append(pn.sem(j[0]))
##                        print 'j[0]'," ",j[0]
##
##                        print 'prop list'," ",PropNoun_list
##                        special_word_noun=j
                    if par[i].label()=='NN' or par[i].label()=='NNS' :
##                        special_word_noun=j
                        special_word_noun.append(j)

                    if par[i].label()=='JJS' or par[i].label()=='JJ':
##                        special_word_adj=j
                        special_word_adj.append(j)
                    if par[i].label()=='CD':
                        year=j
                    if par[i].label()=='IN':
##                        special_word_prep=j
                        special_word_prep.append(j)
                    if par[i].label()=='VBZ' or par[i].label()=='VBD' or par[i].label()=='VBN' or par[i].label()=='VB' or par[i].label()=='VBP' or par[i].label()=='VBG':
                        special_word_verb.append(j)



##                    if par[i].label()=='SBARQ' or par[i].label()=='VP+SQ' or par[i].label()=='SQ+VP+VP':
##                        SELECT+=" count(*) "

                    
                else:
##                    if j.label()=='NN' or j.label()=='NNS' or j.label()=='NNP' or j.label()=='NNPS':
                    if j.label()=='NNP' or j.label()=='NNPS'or j.label()=='NNS':
##                    if par[i].label()=='NN' or par[i].label()=='NNS' :
                        pn=ProperNoun()
##                            pn.sem(j)
##                        print 'j1'," ",j
##                        print 'par[i].label()'," ",par[i].label()
                        PropNoun_list.append(pn.sem(j[0]))
##                        PropNoun_list.add(pn.sem(j[0]))
##                        print 'j2[0]'," ",j[0]
##                        print 'prop list'," ",PropNoun_list
##                        special_word_noun=j[0]
                    if j.label()=='NN' or j.label()=='NNS' :
##                        special_word_noun=j[0]
                        special_word_noun.append(j[0])

                    if j.label()=='JJS' or par[i].label()=='JJ':
                        special_word_adj.append(j[0])

                    if j.label()=='CD':
                            year=j[0]

                    if j.label()=='IN':
                            special_word_prep.append(j[0])

                    if j.label()=='VBZ' or j.label()=='VBD' or j.label()=='VBN' or j.label()=='VB' or j.label()=='VBP' or j.label()=='VBG':
                            special_word_verb.append(j[0])

                    if j.label()=='WRB':
                        #print "Fla when"
                        flag_when = True
                    if(flag==False):
                        s2=par[i].label()+"---->"
                        flag=True
##                        if par[i].label()=='NN' or par[i].label()=='NNS' or par[i].label()=='NNP' or par[i].label()=='NNPS':
                        if par[i].label()=='NNP' or par[i].label()=='NNPS'or par[i].label()=='NNS':
##                        if par[i].label()=='NN' or par[i].label()=='NNS' :
                            pn=ProperNoun()
##                            pn.sem(j)
##                            print 'j1'," ",j
##                            print 'par[i].label()'," ",par[i].label()
                            PropNoun_list.append(pn.sem(j))
                            PropNoun_list.append(pn.sem(j[0]))
##                            PropNoun_list.add(pn.sem(j))
##                            PropNoun_list.add(pn.sem(j[0]))
##                            print 'j2[0]'," ",j[0]
##                            print 'prop list'," ",PropNoun_list
##                            special_word_noun=j
                        if par[i].label()=='NN' or par[i].label()=='NNS' :
##                            special_word_noun=j
                            special_word_noun.append(j[0])

##                        if j.label()=='NN' or j.label()=='NNS' or j.label()=='NNP' or j.label()=='NNPS':
##                            print "NOUN"," ",j
##                            print 'j3'," ",j
##                            print 'j3[0]'," ",j[0]
##                            print 'par[i].label()'," ",par[i].label()
##                            pn=ProperNoun()
####                        pn.sem(j)
##                            PropNoun_list.append(pn.sem(j[0]))
##                            print 'prop list'," ",PropNoun_list
                        if par[i].label()=='JJS' or par[i].label()=='JJ':
                            special_word_adj.append(j)
                        if par[i].label()=='CD':
                            year=j
                        if par[i].label()=='IN':
                            special_word_prep.append(j)
                        if par[i].label()=='VBZ' or par[i].label()=='VBD' or par[i].label()=='VBN' or par[i].label()=='VB' or par[i].label()=='VBP' or par[i].label()=='VBG':
                            special_word_verb.append(j)



##                        if par[i].label()=='SBARQ' or par[i].label()=='VP+SQ' or par[i].label()=='SQ+VP+VP':
##                            SELECT+=" count(*) "

                    
                    s2=s2+j.label()+" "
                    flag2=True
            else:
                if(flag==False):
##                    print 'j 5.label()'," ",j.label()
                    s2=par[i].label()+"---->"
                    flag=True
                    s2=s2+j.label()+" "
##                    if par[i].label()=='SBARQ' or par[i].label()=='VP+SQ' or par[i].label()=='SQ+VP+VP':
##                        SELECT+=" count(*)"

                elif(flag==True):
                    s2=s2+j.label()+" "

                GrammarRulesAndSemAttach_geo(j)

##        if(flag2==True):

##            print s2
##
##    print s

##    vb=Verb()
##    FROM1,WHERE1=vb.sem(PropNoun_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year)
##    print "from"," ",FROM1,"WHERE"," ",WHERE1
    if flag_last==True:
        if flag_wh == False:
            vb=Verb_geo()
            FROM1,WHERE1=vb.sem(PropNoun_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year)
        elif flag_wh == True:
            vb=Verb_geo()
            FROM1,WHERE1=vb.sem_wh(PropNoun_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year)


##        FINALSEM = "select" + " " + SELECT + FROM + "where" + WHERE;

        FINALSEM = SELECT + FROM + WHERE;

##        print FINALSEM

    return FINALSEM
 
 
####-----------------------------------------------------------------------------------------------------------########
####Does semantic attachments of verb for geography sentences and implemneting lambda function a sto set the where clause
####-----------------------------------------------------------------------------------------------------------########

class Verb_geo:

    def sem(self,prop_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year):
        global FROM
        global WHERE
        check=[]
        
        flag00=False
        temp=None
        if 'DiCaprio' in special_word_adj:
            special_word_adj.remove('DiCaprio');
            prop_list.append('DiCaprio')
        elif 'DiCaprio' in special_word_verb:
            special_word_verb.remove('DiCaprio');
            prop_list.append('DiCaprio')
        elif 'DiCaprio' in special_word_prep:
            special_word_prep.remove('DiCaprio');
            prop_list.append('DiCaprio')
        for prop in prop_list:
            check=QueryMovieDB_geo(prop)
            if (check==0 or check==1 )and 'capital' in special_word_noun :
                if (len(FROM) <7):
                    
                    temp=prop
                    #where Co.name like '%Italy%' and Ci.name = 'Rome'
                    FROM+=' capitals Ca inner join countries Co on Ca.CountryId = Co.id inner join  Cities Ci on Ca.CityId = ci.id '
                if (check==0):
                    strr="Co.name like '%"+prop+"%'"
                else:
                    strr="Ci.name like '%"+prop+"%'"
                if (len(WHERE) <=7):
                    WHERE+=strr
                else:
                    WHERE+= "and "+strr
                flag00=True
            elif check==2 or check==0  :
                #Select count(*) from where Con.continent like '%Europe%' and Co.name like '%France%';
                if (len(FROM) <7):
                    #where Co.name like '%Italy%' and Ci.name = 'Rome'
                    FROM+=' CountryContinents Cc inner join countries Co on Cc.CountryId = Co.id inner join  Continents Con on Cc.ContinentId = Con.id  '
                if (check==0):
                    strr="Co.name like '%"+prop+"%'"
                else:  
                    strr="Con.Continent like '%"+prop+"%'"
                if (len(WHERE) <=7):
                    WHERE+=strr
                else:
                    WHERE+= "and "+strr
            
        return FROM,WHERE


############################################################################################################################################

    def sem_wh(self,prop_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year):
        global FROM
        global WHERE
        global SELECT

##        FROM=""
##        WHERE=""
        check=[]
        flag_start=False
        flag0=False
        global flag_when
        for prop in prop_list:
            check=QueryMovieDB_geo(prop)
            if flag_start==False and check==0  :
                SELECT = "Select ci.name"
                FROM+=' capitals Ca inner join countries Co on Ca.CountryId = Co.id inner join Cities Ci on Ca.CityId = ci.id  '
                strr= "Co.name like '%"+prop+"%'"
                WHERE+=strr
                flag_start==True
                flag0=True
                #Select count(*) from capitals Ca inner join countries Co on Ca.CountryId = Co.id inner join  Cities Ci on Ca.CityId = ci.id 
                #where Co.name like '%Italy%' and Ci.name = 'Rome';
            elif check == 1:
                 SELECT = "Select Co.name"
                 FROM+=' capitals Ca inner join countries Co on Ca.CountryId = Co.id inner join  Cities Ci on Ca.CityId = ci.id '
                 strr= "Ci.name like '%"+prop+"%'"
                 WHERE+=strr
            check=-1
        if len(prop_list) ==0:
             
             if 'won' in special_word_verb or 'win' in special_word_verb:
                Otype = ""
                
                          
                if len(special_word_noun) ==1 :
                    
                    Otype = special_word_noun[0]
                else:
                    for i in special_word_noun:
                        if i != 'oscar':
                            Otype = i
                if flag_when == False: 
                    if Otype == 'movie' :
                        Otype = "PICTURE"
                        SELECT = "Select M.NAME"
                        FROM+=' Movie M INNER JOIN Oscar O ON M.id=O.movie_id '
                    else:
                        FROM+=' Person P INNER JOIN Oscar O ON P.id=O.person_id '
                    strr = "O.type like '%BEST-"+Otype+"%'"
                    WHERE+=strr
                    flag_start==True
                    flag0=True
    ##                print 'test13'
                    if year is not None:
                        WHERE +="AND O.YEAR LIKE '%"+year+"%'"
                elif flag_when ==True and 'win' in special_word_verb and len(special_word_adj) != 0:
                    pob = ""
                    if special_word_adj[0] in pob_dict.keys():
                        pob = pob_dict[special_word_adj[0]]
                     
                    SELECT = "Select O.year"
                    FROM+=' Oscar O  INNER JOIN Person P ON P.id = O.person_id '
                    strr="P.pob like '%"+pob+"%' and O.type like'BEST-"+Otype+"'"
                    WHERE+=strr
                    flag_when =False
             elif "directed" in special_word_verb:
                Otype = ""
##                print "direct check"
                
                if 'actor' in special_word_noun:
                    Otype='actor'
                elif 'director' in special_word_noun:
                    Otype='director'
                elif 'actress' in special_word_noun:
                    Otype='actress'
                elif 'movie' in special_word_noun:
                    Otype='movie'


##                Otype = special_word_noun
                if Otype=='movie':
                    Otype = "PICTURE"
                   
                FROM+=' Person P INNER JOIN DIRECTOR D ON P.id=D.director_id INNER JOIN Oscar O ON D.movie_id=O.movie_id '
                
                strr = "O.type like '%BEST-"+Otype+"%'"
                WHERE+=strr
##                print "direct test"
                if year is not None:
                    WHERE +="AND O.YEAR LIKE '%"+year+"%'"
            
             
             else:
                 FROM = ""
                 WHERE= ""
             check=-1
       
        return FROM,WHERE



####queries DB of geo
def QueryMovieDB_geo(str_check):
  

    check=0
    sqlite_file1 = 'WorldGeography.sqlite'        
    table_name1 = 'Cities'   # name of the table to be queried
    attribute = 'name'
    table_name2 = 'Contries'
    table_name3 = 'Continents'# name of the table to be queried
    conn1 = sqlite3.connect(sqlite_file1)
    cursor1 = conn1.cursor()
    attr_value1 = "%"+str_check                        

    cursor1.execute("select name from Cities where name like :at ",{"at":attr_value1})
    exist1=cursor1.fetchall()
    cursor1.execute("select name from Countries where name like :at ",{"at":attr_value1})
    exist2=cursor1.fetchall()
    cursor1.execute("select Continent from Continents where continent like :at ",{"at":attr_value1})
    exist3=cursor1.fetchall()
    

    
    number_of_rows1 =len(exist1)
    number_of_rows2 =len(exist2)
    number_of_rows3 =len(exist3)


    if number_of_rows1 > 0:
        check=1
    elif number_of_rows2 > 0:
        check=0
    elif number_of_rows3 > 0:
        check=2
    


    return check
        

####returns answer from DB of new geo query (SQL QUERY CREATION)

def NewQuery_geo(query):
##    print 'query'," ",query
##    check=0
    check =""
    try:
        sqlite_file_new = 'WorldGeography.sqlite'
        conn_new = sqlite3.connect(sqlite_file_new)
        cursor_new = conn_new.cursor()
        cursor_new.execute(query)
        exist_new=cursor_new.fetchall()
    ##    print 'exist_new'," ",exist_new
    ##    exist_new=cursor_new.fetchone()
        number_of_rows_new =len(exist_new)
    ##    print "number of rows",number_of_rows_new
            
        if number_of_rows_new > 0:
    
            if flag_wh ==True:
                check = exist_new[0][0]
    ##            print exist_new[0]
                if type(check)==int:
                    check=str(check)
    
    ##        else:
    ##            check=1
    
            elif flag_wh ==False:
                if exist_new[0][0] >0:
    ##        print 'exist_new[0]'," ",exist_new[0] 
                    check='yes'
                else:
                    check='no'
    #except (RuntimeError, TypeError, NameError):
    except Exception, e:
        pass
##    print 'check query'," ",check

    return check

####traverses the parse tree and calls semantic attachments method of music sentences
def GrammarRulesAndSemAttach_music(par):
    global SELECT

##    print 'prop list'," ",PropNoun_list
    s=par.label()+"--->"

    global special_word_noun
    global special_word_verb
    global special_word_adj
    global special_word_prep
    global year
    global flag_wh
    global flag_when

    FINALSEM=None
##    year=None
    flag_last=False
    flag_when = False

    #print "qtype ",par[0].label()
    if par[0].label()=="WHNP" or par[0].label()=="WHADVP":
        SELECT+=" P.NAME"
##        print par[0][0].label()
        flag_last =True
        flag_wh = True
    elif par[0].label()=='SQ' or par[0].label()=='VBZ' or par[0].label()=='VBD'or  par[0].label()=='VP':
        SELECT+=" count(*) "
        flag_last=True
        flag_wh = False
        flag_when = False



    for i in range(len(par)):
        flag=False
        flag2=False
        s=s+par[i].label()+" "
        for j in par[i]:
            
            if (isinstance(j[0],str)):
                if (isinstance(j,str)):
                    if par[i].label()=='NNP' or par[i].label()=='NNPS'or par[i].label()=='NNS' or  par[i].label()=='NN':
                        pn=ProperNoun()
                        
                         
                        PropNoun_list.append(pn.sem(j))
                     
                    if par[i].label()=='NN' or par[i].label()=='NNS' :
##                        special_word_noun=j
                        special_word_noun.append(j)

                    if par[i].label()=='JJS' or par[i].label()=='JJ':
##                        special_word_adj=j
                        special_word_adj.append(j)
                    if par[i].label()=='CD':
                        year=j
                    if par[i].label()=='IN':
##                        special_word_prep=j
                        special_word_prep.append(j)
                    if par[i].label()=='VBZ' or par[i].label()=='VBD' or par[i].label()=='VBN' or par[i].label()=='VB' or par[i].label()=='VBP' or par[i].label()=='VBG':
                        special_word_verb.append(j)
                    
                else:
##                    if j.label()=='NN' or j.label()=='NNS' or j.label()=='NNP' or j.label()=='NNPS':
                    if j.label()=='NNP' or j.label()=='NNPS'or j.label()=='NNS' or  j.label()=='NN':
                        pn=ProperNoun()
                        PropNoun_list.append(pn.sem(j[0]))
                    if j.label()=='NN' or j.label()=='NNS' :
##                        special_word_noun=j[0]
                        special_word_noun.append(j[0])

                    if j.label()=='JJS' or par[i].label()=='JJ':
                        special_word_adj.append(j[0])

                    if j.label()=='CD':
                            year=j[0]

                    if j.label()=='IN':
                            special_word_prep.append(j[0])

                    if j.label()=='VBZ' or j.label()=='VBD' or j.label()=='VBN' or j.label()=='VB' or j.label()=='VBP' or j.label()=='VBG':
                            special_word_verb.append(j[0])

                    if j.label()=='WRB':
                        #print "Fla when"
                        flag_when = True
                    if(flag==False):
                        s2=par[i].label()+"---->"
                        flag=True
##                        if par[i].label()=='NN' or par[i].label()=='NNS' or par[i].label()=='NNP' or par[i].label()=='NNPS':
                        if par[i].label()=='NNP' or par[i].label()=='NNPS'or par[i].label()=='NNS':
##                        if par[i].label()=='NN' or par[i].label()=='NNS' :
                            pn=ProperNoun()
##                            pn.sem(j)
##                            print 'j1'," ",j
##                            print 'par[i].label()'," ",par[i].label()
                            PropNoun_list.append(pn.sem(j))
                            PropNoun_list.append(pn.sem(j[0]))
                        if par[i].label()=='NN' or par[i].label()=='NNS' :
##                            special_word_noun=j
                            special_word_noun.append(j[0])

                        if par[i].label()=='JJS' or par[i].label()=='JJ':
                            special_word_adj.append(j)
                        if par[i].label()=='CD':
                            year=j
                        if par[i].label()=='IN':
                            special_word_prep.append(j)
                        if par[i].label()=='VBZ' or par[i].label()=='VBD' or par[i].label()=='VBN' or par[i].label()=='VB' or par[i].label()=='VBP' or par[i].label()=='VBG':
                            special_word_verb.append(j)


                    
                    s2=s2+j.label()+" "
                    flag2=True
                    
            else:
                if(flag==False):
                    s2=par[i].label()+"---->"
                    flag=True
                    s2=s2+j.label()+" "

                elif(flag==True):
                    s2=s2+j.label()+" "

                              
                GrammarRulesAndSemAttach_music(j)

    if flag_last==True:
        if flag_wh == False:
            
            vb=Verb_music()
            FROM1,WHERE1=vb.sem(PropNoun_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year)
        elif flag_wh == True:
            vb=Verb_music()
            FROM1,WHERE1=vb.sem_wh(PropNoun_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year)


##        FINALSEM = "select" + " " + SELECT + FROM + "where" + WHERE;
        if len(FROM) == 0 or len(WHERE) == 0:
            SELECT = ""
        FINALSEM = SELECT + FROM + WHERE;

##        print FINALSEM

    return FINALSEM
 

####-----------------------------------------------------------------------------------------------------------########
####Does semantic attachments of verb for MUSIC sentences and implemneting lambda function a sto set the where clause
####-----------------------------------------------------------------------------------------------------------########
class Verb_music:

    def sem(self,prop_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year):
        global FROM
        global WHERE
##        if 'actor' in special_word_noun:
##            print 'yes actor'
        
##        FROM=""
##        WHERE=""
        check=[]
        flag00=False
        temp=None
        #print "in sem", prop_list
        for prop in prop_list:
            check=QueryMovieDB_music(prop)
            #print 'check'," ",check, "noun = ",prop
            if (check==2 or check==0 )and 'sing' in special_word_verb:
                if (len(FROM) <7):
                    
                    temp=prop
                    #where Co.name like '%Italy%' and Ci.name = 'Rome'
                    FROM+=' Artist A Inner join album Al on A.id = Al.artsitID Inner join Track t on t.albumID = Al.albumID  '
                if (check==0):
                    strr=" A.name  like '%"+prop+"%'"
                else:
                    strr="t.name like '%"+prop+"%'"
                if (len(WHERE) <=7):
                    WHERE+=strr
                else:
                    WHERE+= "and "+strr
                flag00=True
            elif check==2 or check==1  and 'album' in special_word_noun:
                #Select count(*) from where Con.continent like '%Europe%' and Co.name like '%France%';
                if (len(FROM) <7):
                    #select * from Album Al Inner join Track t on t.albumID = Al.albumID where Al.name  like '%Thriller%' and t.name like '%Beat It%';

                    temp=prop
                    #where Co.name like '%Italy%' and Ci.name = 'Rome'
                    FROM+=' Album Al Inner join Track t on t.albumID = Al.albumID   '
                if (check==1):
                    strr="Al.name  like '%"+prop+"%'"
                else:
                    strr="t.name like '%"+prop+"%'"
                if (len(WHERE) <=7):
                    WHERE+=strr
                else:
                    WHERE+= "and "+strr
                flag00=True
            elif (check== 0 or check == 4) and 'born' in special_word_verb:
                #print "in verb" 
                if len(FROM) <7 :
                    FROM += 'Artist'
                if check == 0:
                    str ="name like '%"+prop+"%'"
                else:
                    str  = "placeOfBith like '%"+prop+"%'"
                if len(WHERE) <=7:
                    WHERE += str
                else:
                    WHERE += " and "+str
            '''
            else:
                
                FROM = ""
                WHERE= ""
            '''
            check = -1
        return FROM,WHERE


############################################################################################################################################

    def sem_wh(self,prop_list,special_word_noun,special_word_verb,special_word_adj,special_word_prep,year):
        global FROM
        global WHERE
        global SELECT

##        FROM=""
##        WHERE=""
        check=[]
        flag_start=False
        flag0=False
        flag00=False
        flag1=False
        flag2=False
        flag3=False
        flag3_0=False
        flag4=False
        flag4_1=False
        temp=None
        global flag_when
       
        for prop in prop_list:
            check=QueryMovieDB_music(prop)
            if (check==2 or check==0 and 'singer' in special_word_noun):
                print "in check",FROM
                SELECT = "Select A.name"  ;
                FROM +=' Artist A Inner join album Al on A.id = Al.artsitID Inner join Track t on t.albumID = Al.albumID '
                strr= "t.name like '%"+prop+"%'"
                WHERE+=strr
                flag_start==True
                flag0=True
           
            check=-1
       
        return FROM,WHERE



####queries DB of music 

def QueryMovieDB_music(str_check):
  

    check=-1
    sqlite_file1 = 'music.sqlite'        
   
    conn1 = sqlite3.connect(sqlite_file1)
    cursor1 = conn1.cursor()
    cursor3 = conn1.cursor()
    attr_value1 = "%"+str_check+"%"                       
    last_name ="% "+str_check
    first_name = str_check+" %"
    only_name = str_check
    ##--- query to check first name last name or only if one name is given
    cursor1.execute("select name from Artist where name like :fn or name like :ln or name like :on ",{"fn":first_name,"ln":last_name,"on":only_name})
    exist1=cursor1.fetchall()
    cursor1.execute("select name from Album  where name like :at ",{"at":attr_value1})
    exist2=cursor1.fetchall()
    #sql1 = "select name from Track where name like "+attr_value1
    cursor3.execute("select name from Track where name like :at ",{"at":attr_value1})
    exist3=cursor3.fetchall()
    ##print "hello ", sql1, len(exist3)
    cursor1.execute("select name from Genres where name like :at ",{"at":attr_value1})
    exist4=cursor1.fetchall()
    
    cursor1.execute("select placeOfBith from Artist where placeOfBith like :at ",{"at":attr_value1})
    exist5=cursor1.fetchall()

    number_of_rows1 =len(exist1)
    number_of_rows2 =len(exist2)
    number_of_rows3 =len(exist3)
    number_of_rows4 =len(exist4)
    number_of_rows5 =len(exist5)

    if number_of_rows1 > 0:
        check=0
    elif number_of_rows2 > 0:
        check=1
    elif number_of_rows3 > 0:
        check=2
    
    elif number_of_rows4 > 0:
        check=3
    
    elif number_of_rows5 > 0:
        check=4

    return check
        

####returns answer of music query from DB (SQL QUERY CREATION)

def NewQuery_music(query):
##    print 'query'," ",query
##    check=0
    check =""
    try:
        sqlite_file_new = 'music.sqlite'
        conn_new = sqlite3.connect(sqlite_file_new)
        cursor_new = conn_new.cursor()
        cursor_new.execute(query)
        exist_new=cursor_new.fetchall()
    ##    print 'exist_new'," ",exist_new
    ##    exist_new=cursor_new.fetchone()
        number_of_rows_new =len(exist_new)
    ##    print "number of rows",number_of_rows_new
            
        if number_of_rows_new > 0:
    
            if flag_wh ==True:
                check = exist_new[0][0]
    ##            print exist_new[0]
                if type(check)==int:
                    check=str(check)
    
    ##        else:
    ##            check=1
    
            elif flag_wh ==False:
                if exist_new[0][0] >0:
    ##        print 'exist_new[0]'," ",exist_new[0] 
                    check='yes'
                else:
                    check='no'
    #except (RuntimeError, TypeError, NameError):
    except Exception, e:
        pass
##    print 'check query'," ",check

    return check

#module for doing named entity recognition
def chunking_NER(sent,flag):

    #STANFORD NER TAGGER
    if flag=='stanford':
        #from nltk.tag.stanford import NERTagger
        java_path = "C:/Program Files/Java/jdk1.8.0_60/bin/java.exe"
        os.environ['JAVAHOME'] = java_path
        st = NERTagger('C:/Python27(32bit)/Lib/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz','C:/Python27(32bit)/Lib/stanford-ner-2014-06-16/stanford-ner.jar')
        ner_list = st.tag(sent.split())

    #NLTK NE TAGGER
    else:
        ner_list=[]
        sentences = nltk.word_tokenize(sent)
        sentences = nltk.pos_tag(sentences)
        grammar = r"""
          NP:
        {<.*>+}          # Chunk everything
        }<VBD|IN>+{      # Chink sequences of VBD and IN
        """
        cp = nltk.RegexpParser(grammar)

        result = cp.parse(sentences)
        version  = nltk.__version__
        if version[0] =='3':        
            for chunk in nltk.ne_chunk(sentences):
                if hasattr(chunk, 'label'):
                    for c in chunk.leaves():
                        ner_list.append((c[0],chunk.label()))
                else:
                    ner_list.append((chunk[0],chunk[1]))
        else:
            for chunk in nltk.ne_chunk(sentences):
                if hasattr(chunk, 'node'):
                    for c in chunk.leaves():
                        ner_list.append((c[0],chunk.label()))
            
    return ner_list



    

#module for extracting words from files
def makeLexList(mu_vf, mu_nf, mo_vf, mo_nf, geo_vf, geo_nf,geo_pp,amb):

    mu_vf_r = open(mu_vf, 'r')
    mu_nf_r = open(mu_nf, 'r')
    mo_vf_r = open(mo_vf, 'r')
    mo_nf_r = open(mo_nf, 'r')
    geo_vf_r = open(geo_vf, 'r')
    geo_nf_r = open(geo_nf, 'r')
    geo_pp_r = open(geo_pp,'r')
    amb_r = open(amb, 'r')

    #Create a list of words in the sentence, within a tuple.
    for word in mu_vf_r:
        #word=word.encode('utf-8')
        word_filter = [i.lower() for i in word.split()]
        mu_vf_list.extend(word_filter)
    for word in mu_nf_r:
        #word=word.encode('utf-8')
        word_filter = [i.lower() for i in word.split()]
        mu_nf_list.extend(word_filter)
    for word in mo_vf_r:
        #word=word.encode('utf-8')
        word_filter = [i.lower() for i in word.split()]
        mo_vf_list.extend(word_filter)
    for word in mo_nf_r:
        #word=word.encode('utf-8')
        word_filter = [i.lower() for i in word.split()]
        mo_nf_list.extend(word_filter)
    for word in geo_vf_r:
        #word=word.encode('utf-8')
        word_filter = [i.lower() for i in word.split()]
        geo_vf_list.extend(word_filter)
    for word in geo_nf_r:
        #word=word.encode('utf-8')
        word_filter = [i.lower() for i in word.split()]
        geo_nf_list.extend(word_filter)
    for word in geo_pp_r:
        #word=word.encode('utf-8')
        word_filter = [i.lower() for i in word.split()]
        geo_pp_list.extend(word_filter)
    for word in amb_r:
        #word=word.encode('utf-8')
        word_filter = [i.lower() for i in word.split()]
        amb_list.extend(word_filter)



    return mu_vf_list,mu_nf_list,mo_vf_list,mo_nf_list,geo_vf_list,geo_nf_list,geo_pp_list,amb_list




#module for labeling with appropriate category
def label_cat(sampFile):


##    sf = open(sampFile, 'r')
##    sampTxt = sf.readlines()
    sqlite_file1 = 'oscar-movie_imdb.sqlite'
    sqlite_file2 = 'music.sqlite'
    sqlite_file3 = 'WorldGeography.sqlite'
    
    table_name1 = 'Person'   # name of the table to be queried
    attribute1 = 'name'
    table_name2 = 'Artist'   # name of the table to be queried
    attribute2 = 'name'


##    for sent1 in sampTxt:
        
    test=parseSentences(sampFile)
##    print '<QUESTION>',sent1
    list_test=[word for word,pos in test.pos() if pos=='VB' or pos=='VBG' or pos=='VBP' or pos=='VBN' or pos=='VBD' or pos=='VBZ']
    list_test_noun=[word for word,pos in test.pos() if pos=='NN' or pos=='NNP' or pos=='NNS' or pos=='NNPS']
    list_test_prep=[word for word,pos in test.pos() if pos=='IN' ]

    flag=False
    count=0
    cat = ""

    #verb check
    for v_pos in list_test:
        count+=1
        if v_pos in mu_vf_list:
            #print "<CATEGORY> music"
            cat='music'
            flag=True
            break
        elif v_pos in mo_vf_list:
            #print "<CATEGORY> movie"
            cat='movie'
            flag=True
            break
        elif v_pos in geo_vf_list:
            #print "<CATEGORY> geography"
            cat='geography'
            flag=True
            break
        elif v_pos in amb_list:
            ner_list_tup=chunking_NER(sampFile,'nltk')
            for (word,entity) in ner_list_tup:
                if entity=='PERSON' or entity=='ORGANIZATION':
                    attr_value=word
                    conn1 = sqlite3.connect(sqlite_file1)
                    conn2 = sqlite3.connect(sqlite_file2)
                    cursor1 = conn1.cursor()
                    cursor2 = conn2.cursor()
                    attr_value1 = "%"+attr_value                        
                    cursor1.execute("select name from Person where name like :at ",{"at":attr_value1})
                    cursor2.execute("select name from Artist where name like :at ",{"at":attr_value1})
                    exist1=cursor1.fetchall()
                    number_of_rows1 =len(exist1)

                    if number_of_rows1 >0:
                            #print "<CATEGORY> movie"
                            cat='movie'
                            flag = True
                            break
                    exist2=cursor2.fetchall()
                    number_of_rows2 = len(exist2)
                    if number_of_rows2 >0:                                
                        #print "<CATEGORY> music"
                        cat='music'
                        flag = True
                        break
                    
    ## prep check
    if flag == False :
        count_pp = 0
        flagpp =False
        for n_pp in list_test_prep:
            count_pp+=1                    
            if n_pp in geo_pp_list:
                ner_list_tup=chunking_NER(sampFile,'NLTK')
                sent2 = sampFile.lower()
                tokenized_sentence = nltk.word_tokenize(sent2)
                index_pp =tokenized_sentence.index(n_pp)
                if index_pp+1<len(ner_list_tup) and index_pp >0:
                    if (ner_list_tup[index_pp -1][1]=='LOCATION' and ner_list_tup[index_pp+1][1] =='LOCATION' )or ( ner_list_tup[index_pp -1][1]=='GPE' and  ner_list_tup[index_pp+1][1] =='GPE'):
                        #print "<CATEGORY> geography"
                        cat='geography'
                        flagpp=True
                        break

        
        if count_pp==len(list_test_prep) and flagpp==False :
            count1=0
            flag1=False

            #noun check
            for n_pos in list_test_noun:
                count1+=1
                if n_pos in mu_nf_list:
                    #print "<CATEGORY> music"
                    cat='music'
                    flag1=True
                    break
                elif n_pos in mo_nf_list:
                    #print "<CATEGORY> movie"
                    cat='movie'
                    flag1=True
                    break
                elif n_pos in geo_nf_list:
                    #print "<CATEGORY> geography"
                    cat='geography'
                    flag1=True
                    break
                elif count1==len(list_test_noun) and flag==False and flag1 == False :
                    ner_list_tup=chunking_NER(sampFile,'NLTK')
                    flag_geo2=False
                    #print "in location check 1",entity
                    for (word,entity) in ner_list_tup:
                        #print "in location check 1",entity
                        if entity=='LOCATION' or entity=='GPE':
                            flag_geo2=True
                            print "<CATEGORY> geography"
                            cat='geography'
                            break

                    if not flag_geo2:
                        flag_final=False
                        ner_list_tup=chunking_NER(sampFile,'nltk')                       
                        for (word,entity) in ner_list_tup:
                            if entity=='PERSON' or entity=='ORGANIZATION':
                                attr_value=word
                                conn1 = sqlite3.connect(sqlite_file1)
                                conn2 = sqlite3.connect(sqlite_file2)
                                cursor1 = conn1.cursor()
                                cursor2 = conn2.cursor()
                                len_attr = len(attr_value)
                                attr_value1 = "%"+attr_value
                                cursor1.execute("select name from Person where name like :at ",{"at":attr_value1})
                                cursor2.execute("select name from Artist where name like :at ",{"at":attr_value1})                                    
                                exist1=cursor1.fetchall()                                                               
                                number_of_rows1 =len(exist1)
                                if number_of_rows1 >0:
                                        print "<CATEGORY> movie"
                                        cat='movie'
                                        flag_final=True
                                        break
                                exist2=cursor2.fetchall()
                                number_of_rows2 = len(exist2)
                                if number_of_rows2 >0:
                                    print "<CATEGORY> music"
                                    cat='music'
                                    flag_final=True
                                    break
                        if flag_final == False:
                            ## -- No Label Found
                            print "<CATEGORY> No Category Found"
                            cat='not found'


    return cat







####checks nltk version
def version_check():
     version  = nltk.__version__
     if version[0] =='3':
         tagname = ".label()"
     else:
         tagname = "node"


def printSQL():

    #TODO update this to get and print appropriate SQL
    global currentQuery
    par=parseSentences(currentQuery)
    sem_query=GrammarRulesAndSemAttach(par)
    global sqlQuery
    sqlQuery = sem_query # map currentQuery to sqlQuery
    print("<SQL>\n" , sqlQuery)
    print("\n");

def printSQL_geo():

    #TODO update this to get and print appropriate SQL
    global currentQuery
    par=parseSentences(currentQuery)
    sem_query=GrammarRulesAndSemAttach_geo(par)
    global sqlQuery
    sqlQuery = sem_query # map currentQuery to sqlQuery
    print("<SQL>\n" + sqlQuery)
    print("\n");

def printSQL_music():

    #TODO update this to get and print appropriate SQL
    global currentQuery
    par=parseSentences(currentQuery)
    sem_query=GrammarRulesAndSemAttach_music(par)
    global sqlQuery
    sqlQuery = ""
    sqlQuery = sem_query # map currentQuery to sqlQuery
    print "<SQL>\n"
    print  sqlQuery
    print("\n");



def printAnswer():

    # execute sqlQuery in order to generate appropriate natural language response
    global sqlQuery
    answer = NewQuery(sqlQuery); 
    if len(answer) !=0: 
        print("<ANSWER>\n" + answer)
    else:
        print "No answer found"

def printAnswer_music():

    # execute sqlQuery in order to generate appropriate natural language response
    global sqlQuery
    answer = NewQuery_music(sqlQuery); 
    if len(answer) !=0: 
        print("<ANSWER>\n" + answer)
    else:
        print "No answer found"

def printAnswer_geo():

    # execute sqlQuery in order to generate appropriate natural language response
    global sqlQuery
    answer = NewQuery_geo(sqlQuery); 
    if len(answer) !=0: 
        print("<ANSWER>\n" + answer)
    else:
        print "No answer found"





def main():
    print("Welcome! This is MiniWatson. \n")
    print("Please ask a question. Type 'q' when finished. \n")
    print("\n");

##    inputString =str( input("").strip(" "))
    inputString =raw_input("").strip(" ").strip('\"')
    print "hi ",inputString
    if len(inputString) == 0:
        print "Invalid input"
        inputString =raw_input("").strip(" ").strip('\"')
        print "hi ",inputString
    #inputString =str(raw_input())
    #inputString=unicode(inputString, errors='replace')
    global currentQuery
    makeLexList('music_verb.txt', 'music_noun.txt', 'movie_verb.txt', 'movie_noun.txt', 'geo_verb.txt', 'geo_noun.txt','geo_pp.txt','ambiguous_words.txt')
    while inputString != "q": 
         
         currentQuery = inputString;
         print("<QUERY>\n" + currentQuery);
         print("\n");
         del PropNoun_list[:]
         global SELECT
         SELECT=" select "
         global FROM
         FROM=" from "
         global WHERE
         WHERE=" where "
         global year
         del special_word_noun[:]
         del special_word_verb[:]
         del special_word_adj[:]
         del special_word_prep[:]
         year=None
         category=label_cat(inputString)
         print("\n")
         if category=='movie':
             printSQL(); #TODO implement method below
             printAnswer(); #TODO implement method below
         elif category=='music':
             printSQL_music(); #TODO implement method below
             printAnswer_music(); #TODO implement method below
         elif category=='geography':
             printSQL_geo(); #TODO implement method below
             printAnswer_geo(); #TODO implement method below
         else:
            print 'no no'
         print("\n")
##         inputString =str( input("").strip(" "))
         inputString =raw_input("").strip(" ").strip('\"')
         if len(inputString) == 0:
             print "Invalid input"
             inputString =raw_input("").strip(" ").strip('\"')
	
    print("Goodbye. \n");	

if __name__ == '__main__':
    main()

