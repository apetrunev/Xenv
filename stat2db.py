#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import getopt
import time
import csv
import ConfigParser
import MySQLdb

db = None
cursor = None 

def stat2db(statfile, id_campaign):
  stat_ctx = {}
  
  tmp = os.path.basename(statfile) 
  year, month, day, _, _, _ = tmp.split('-')
  date = year + '-' + month + '-' + day
  
  with open(statfile, 'r') as csv_file:
    data = csv.reader(csv_file, delimiter=',')
    keys = []
    values = [] 
    
    for row in data:
      if data.line_num == 1:
        tmp_str = unicode(row[0], "utf-8")
        tmp_str = tmp_str.split(',')[0]
        
        pieces = tmp_str.split('"')
        campaign_description = ""
        for piece in pieces:
          # trim spaces
          piece = piece.strip()
          if campaign_description == "":
            campaign_description = piece
          else:
            campaign_description = campaign_description + " " + piece
      elif data.line_num == 2:
        for col in xrange(3, len(row)):
          key = unicode(row[col], "utf-8")
          keys.append(key)
      elif data.line_num == 3:
        for col in xrange(3, len(row)):
          value = unicode(row[col], "utf-8")
          values.append(value) 
         
    for idx in xrange(1, len(keys)):
      if u'Показы' in keys[idx]:
        stat_ctx['impressions'] = values[idx] 
      elif u'Клики' in keys[idx]:
        stat_ctx['clicks'] = values[idx]
      elif u'Расход' in keys[idx]:
        stat_ctx['expenditure'] = values[idx]
      elif u'Ср. цена клика' in keys[idx]:
        stat_ctx['avg_cpc'] = values[idx]
      elif u'Глубина' in keys[idx]:
        stat_ctx['depth'] = values[idx]
      elif u'Конверсия (%)' in keys[idx]:
        stat_ctx['conversion_percent'] = values[idx]
      elif u'Конверсии' in keys[idx]:
	stat_ctx['conversions'] = values[idx]
      elif u'Рентабельность' in keys[idx]:
        stat_ctx['ROI'] = values[idx]
      elif u'Доход' in keys[idx]:
        stat_ctx['revenue'] = values[idx]
      elif u'Цена цели' in keys[idx]:
        stat_ctx['goal_cost'] = values[idx]
      elif 'CTR' in keys[idx]:
        stat_ctx['ctr'] = values[idx]

    cursor.execute("SELECT id FROM statistic WHERE id_company=\"" + id_campaign + "\" and date=\"" + date + "\" and company_description=\"" + campaign_description + "\"")
    db.commit()
     
    records = cursor.fetchall()
        # insert new records
    if len(records) == 0:
      pattern = """(id_company, date, impressions, clicks, ctr,
                    expenditure, avg_cpc, depth, conversions,
                    conversion_percent, goal_cost, roi, revenue, company_description)"""
      
      cursor.execute("INSERT INTO statistic " + pattern + " VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (id_campaign,
                         date,
                         stat_ctx['impressions'],
                         stat_ctx['clicks'],
                         stat_ctx['ctr'], 
      	                 stat_ctx['expenditure'],
                         stat_ctx['avg_cpc'],
                         stat_ctx['depth'],
                         stat_ctx['conversions'],
                         stat_ctx['conversion_percent'],
                         stat_ctx['goal_cost'],
                         stat_ctx['ROI'],
                         stat_ctx['revenue'],
       		         campaign_description))
      db.commit()
    else:
      pattern = '''impressions=\"%s\", clicks=\"%s\", ctr=\"%s\", expenditure=\"%s\",
                   avg_cpc=\"%s\", depth=\"%s\", conversions=\"%s\", conversion_percent=\"%s\",
                   goal_cost=\"%s\", roi=\"%s\", revenue=\"%s\"'''
  
      query = "UPDATE statistic SET " + pattern + " WHERE id_company=\"" + id_campaign + "\" and DATE=\"" + date +"\" and company_description=\"" + campaign_description + "\""
   
      cursor.execute(query,
                     (stat_ctx['impressions'], 
                     stat_ctx['clicks'],
                     stat_ctx['ctr'],
                     stat_ctx['expenditure'],
                     stat_ctx['avg_cpc'],
                     stat_ctx['depth'],
                     stat_ctx['conversions'],
                     stat_ctx['conversion_percent'],
                     stat_ctx['goal_cost'],
                     stat_ctx['ROI'],
                     stat_ctx['revenue']))
      db.commit()

def main():
  global db, cursor
  try:
    opts, args = getopt.getopt(sys.argv[1:], "", [ "conf=", "file=", "id="])
  except getopt.GetoptError as err:
    print str(err)
    usage()
    sys.exit(1)
  
  ID = ""

  for o, a in opts:
    if o in ("--file"):
      CSV = a
    elif o in ("--conf"):
      CONF = a
    elif o in ("--id"):
      ID = a
    else:
      assert False, "unhandled option"
   
  config = ConfigParser.RawConfigParser()
  config.read(CONF)
  
  user = config.get('Database', 'user')
  password = config.get('Database', 'password')
  host = config.get('Database', 'host')
  database = config.get('Database', 'database')
  download = config.get('Common', 'download')
  
  db = MySQLdb.connect(host=host, user=user, passwd=password, db=database, charset='utf8', use_unicode=True)
  cursor = db.cursor()  
 
  stat2db(CSV, ID)  

  db.close()

if __name__=="__main__":
  main()
