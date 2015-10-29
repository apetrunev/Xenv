#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import getopt
import time
import csv
import types
import ConfigParser
import MySQLdb

db = None
cursor = None 

def get_stat_ctx(statfile, id_campaign):
  stat_ctx = {}
  
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

    return stat_ctx
#
# get statistic per login 
#
 
def get_stat_ctx2(statfile, id_campaign):
  stat_ctx = {}
  
  with open(statfile, 'r') as csv_file:
    data = csv.reader(csv_file, delimiter=',')
    keys = []
    values = []
  
    for row in data:
      # read columns' names
      if data.line_num == 2:
        for col in xrange(2, len(row)):
          key = unicode(row[col], "utf-8")      
          keys.append(key)
      else:
        m = re.search("(^[0-9]+$)", unicode(row[0], 'utf-8'))
        if type(m) == types.NoneType:
          continue
        
        campaign_number = m.group(0)
        for col in xrange(2, len(row)):
          value = unicode(row[col], "utf-8")
          values.append(value)
        
        campaign_number = campaign_number.encode('ascii', 'ignore')
	stat_ctx[campaign_number] = {}

        for idx in xrange(1, len(keys)):
          if u'Показы' in keys[idx]:
            stat_ctx[campaign_number]['impressions'] = values[idx] 
          elif u'Клики' in keys[idx]:
            stat_ctx[campaign_number]['clicks'] = values[idx]
          elif u'Расход' in keys[idx]:
            stat_ctx[campaign_number]['expenditure'] = values[idx]
          elif u'Ср. цена клика' in keys[idx]:
            stat_ctx[campaign_number]['avg_cpc'] = values[idx]
          elif u'Глубина' in keys[idx]:
            stat_ctx[campaign_number]['depth'] = values[idx]
          elif u'Конверсия (%)' in keys[idx]:
            stat_ctx[campaign_number]['conversion_percent'] = values[idx]
          elif u'Конверсии' in keys[idx]:
	    stat_ctx[campaign_number]['conversions'] = values[idx]
          elif u'Рентабельность' in keys[idx]:
            stat_ctx[campaign_number]['ROI'] = values[idx]
          elif u'Доход' in keys[idx]:
            stat_ctx[campaign_number]['revenue'] = values[idx]
          elif u'Цена цели' in keys[idx]:
            stat_ctx[campaign_number]['goal_cost'] = values[idx]
          elif 'CTR' in keys[idx]:
            stat_ctx[campaign_number]['ctr'] = values[idx]

  return stat_ctx

def stat2db(statfile, id_campaign, tablename):
  stat_ctx = {}
  
  tmp = os.path.basename(statfile) 
  year, month, day, _, _, _ = tmp.split('-')
  date = year + '-' + month + '-' + day
  #
  # statistic per campaign
  #
  cstat_ctx = get_stat_ctx2(statfile, id_campaign)
  for campaign_number in cstat_ctx:
    stat_ctx = cstat_ctx[campaign_number]

    query = "SELECT id FROM " + tablename + \
            " WHERE id_company=\"" + id_campaign + \
            "\" and date=\"" + date + \
            "\" and company_description LIKE \"" + campaign_number + "\""
 
    cursor.execute(query)
    db.commit()

    records = cursor.fetchall()
  
    if len(records) == 0:
      pattern = """(id_company, date, impressions, clicks, ctr,
                    expenditure, avg_cpc, depth, conversions,
                    conversion_percent, goal_cost, roi, revenue, company_description)"""
    
      query_fmt = "INSERT INTO " + tablename + " " + pattern + \
                  " VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\")"

      query = query_fmt % (id_campaign,
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
       		           campaign_number) 
       
      cursor.execute(query)
      db.commit()
    else:
      pattern = """impressions=%s, clicks=%s, ctr=%s, expenditure=%s,
                   avg_cpc=%s, depth=%s, conversions=%s, conversion_percent=%s,
                   goal_cost=%s, roi=%s, revenue=%s"""
  
      query = "UPDATE statistic SET " + pattern + \
              " WHERE id_company=\"" + id_campaign + "\" and DATE=\"" + date +"\" and company_description LIKE \"" + campaign_number + "\""
   
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
 
  stat2db(CSV, ID, "login_stat")  

  db.close()

if __name__=="__main__":
  main()
