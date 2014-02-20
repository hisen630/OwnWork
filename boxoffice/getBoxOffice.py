#!/usr/bin/env pyton2.7
#coding=gbk

"""
Get China Mainland box office data from www.m1905.com.
Usage:
    python ./getBoxOffice.py
This script then will start running to get the data, and
store the data(a json format) in a file(boxoffice.txt) under
current directory.
For furthur use, use the Entity.fromJson method to load the data.
"""

import sys
import re
from urllib2 import urlopen
from bs4 import BeautifulSoup
import json

tbody_p = re.compile("<tbody>(.+)</tbody>", re.DOTALL)
row_p = re.compile("<tr class=\"tableCONT\">(.*?)</tr>",re.DOTALL)
td_p = re.compile("<td[^>]+>(.*?)</td>")
charset_p = re.compile("charset=([^\"]+)")
gain_p = re.compile("(\d+)")

URL_TEMPLATE = "http://www.m1905.com/rank/top/14/year-%d-week-%d"
target_url_list = [
    (2010,22,52),
    (2011,1,52),
    (2012,1,52),
    (2013,1,52),
    (2014,1,7)
        ]
# the output file
data_file = "./boxoffice.txt"

class Object(object) :
    def __init__(self) :
        #super(Object, self).__init__() # no need to call object.__init__
        self.name = self.__module__
        self.name += '.' + self.__class__.__name__

    def toString(self) :
        return buildString(self)

    def __str__(self) :
        return self.toString()

class Entity(Object) :
    def __init__(self) :
        super(Entity, self).__init__()

    def object2dict(self, obj):
        #convert object to a dict
        d = {}
        d['__class__'] = obj.__class__.__name__
        d['__module__'] = obj.__module__
        d.update(obj.__dict__)
        return d

    def dict2object(self, d):
        #convert dict to object
        if'__class__' in d:
            class_name = d.pop('__class__')
            module_name = d.pop('__module__')
            module = __import__(module_name)
            class_ = getattr(module, class_name)
            inst = class_()
            inst.__dict__ = dict((key.encode('utf-8'), value) for key, value in d.items())
        else:
            inst = d
        return inst

    def toJson(self) :
        return json.dumps(self, default = self.object2dict)

    # this method has no affect on the self instance
    def fromJson(self, dump) :
        return json.loads(dump, object_hook = self.dict2object)

class Movie(Entity):
    def __init__(self, data_dict):
        super(Movie, self).__init__()
        self.name = data_dict['name']
        self.href = data_dict['href']
        self.actors_list = data_dict['actors_list']
        self.boxoffice = {}

    def add(self, rank, weekly_bo, acc_bo):
        assert weekly_bo[0] == acc_bo[0]
        key = weekly_bo[0]
        week_bo = weekly_bo[1]
        acc_bo = acc_bo[1]
        self.boxoffice[key] = (rank, week_bo, acc_bo)

if '__main__' == __name__:

    movie_dict = {} # moviename_href -> Movie instance

    df = open(data_file, 'w')

    for ele in target_url_list:
        year = ele[0]
        s_week = ele[1]
        e_week = ele[2]
        for week_no in xrange(s_week, e_week+1):
            url = URL_TEMPLATE%(year,week_no)
            print url
            url_stream = urlopen(url)
            html_str = url_stream.read()

            charset_m = charset_p.search(html_str)
            charset = charset_m.group(1)
            
            tbody_m = tbody_p.search(html_str)
            if tbody_m:
                tbody_str = tbody_m.group(1)
                row_m_list = row_p.findall(tbody_str)
                #print row_m_list[0]
                # one line record
                for r in row_m_list:
                    td_list = td_p.findall(r)
                    invalid_flag = False
                    # treat every cell
                    for idx, td in enumerate(td_list):
                        #print >> df,'[debug]',td
                        soup = BeautifulSoup(markup=td, from_encoding=charset)
                        # rank
                        if idx == 0:
                            rank = soup.getText()
                        # name, href
                        elif idx == 1:
                            #print >> df, soup
                            movie_a = soup.find('a')
                            # 2013-20 No.15 has no link
                            if movie_a is None:
                                invalid_flag = True
                                break
                            # when the movie name is too long, text is trimed
                            # so need get the title
                            name = movie_a.get('title')
                            href = movie_a.get('href')
                        # actors
                        elif idx == 2:
                            actors_list = []
                            actors_a_list = soup.findAll('a')
                            for actor_a in actors_a_list:
                                actors_list.append((actor_a.getText(), actor_a.get('href')))
                        # week gain
                        elif idx == 3:
                            week_gain = soup.getText()
                            gain_m = gain_p.search(week_gain)
                            week_gain = gain_m.group(1)
                        # accumuated gain
                        elif idx == 4:
                            acc_gain = soup.getText()
                            gain_m = gain_p.search(acc_gain)
                            if gain_m is not None:
                                acc_gain = gain_m.group(1)
                            else:
                                acc_gain = '0'

                    if invalid_flag:
                        continue
                    
                    name = name.encode('utf-8')
                    data_dict = {}
                    data_dict['name'] = name
                    data_dict['href'] = href
                    data_dict['actors_list'] = actors_list
                    weekly_bo = ('%d_%d'%(year,week_no), week_gain)
                    acc_bo = ('%d_%d'%(year,week_no), acc_gain)
                    key = '_'.join((name.decode('utf-8'), href))
                    if (key) not in movie_dict:
                        movie_dict[key] = Movie(data_dict)
                    movie_dict[key].add(rank,weekly_bo, acc_bo)
                        
    for movie in movie_dict.values():
        print >> df, movie.toJson()
    df.close()
