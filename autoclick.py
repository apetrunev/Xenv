#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import getopt
import random
import time
import csv
import codecs
import subprocess
import ConfigParser
import MySQLdb

from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

# Database
db = None
cursor = None 
# Browser
browser = None

def usage():	
  print "Usage information"

def autoclick(ya_context):
  global browser
  url_auth = "https://passport.yandex.ru/auth"
  url_direct = "https://direct.yandex.ru/registered/main.pl?cmd=showCamps"

  proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': ya_context['proxy'],
    'ftpProxy': ya_context['proxy'],
    'sslProxy': ya_context['proxy'],
    'noProxy' : ''
  })

  stream_type = "application/octet-stream;application/csv;text/csv;application/vnd.ms-excel;"
  profile = webdriver.FirefoxProfile()
  # set custom location
  profile.set_preference('browser.download.folderList', 2)
  profile.set_preference('browser.download.manager.showWhenStarting', False)
  profile.set_preference('browser.download.dir', ya_context['download'])
  profile.set_preference('browser.helperApps.neverAsk.saveToDisk', stream_type)
  profile.set_preference("browser.cache.disk.enable", False);
  profile.set_preference("browser.cache.memory.enable", False);
  profile.set_preference("browser.cache.offline.enable", False);
  profile.set_preference("network.http.use-cache", False);
  
  browser = webdriver.Firefox(proxy=proxy, firefox_profile=profile)
  browser.set_window_size(ya_context['resolution_w'], ya_context['resolution_h'])
  
  browser.get(url_auth)
  # find authentication form
  html_login  = browser.find_element_by_xpath("//input[@id='login']")
  html_passwd = browser.find_element_by_xpath("//input[@id='passwd']")
  html_submit = browser.find_element_by_xpath("//button[@type='submit']")
  # send context 
  html_login.clear()
  html_login.send_keys(ya_context['login'])
  html_passwd.clear()
  html_passwd.send_keys(ya_context['password'])
  html_submit.click()
  # jump to the page with campaigns
  browser.get(url_direct)
  # jump to the page with the statistic
  browser.find_element_by_link_text('Статистика').click()
  # today
  browser.find_element_by_xpath('//span[text() = "сегодня"]').click()
  browser.find_element_by_xpath('(//button[@type="button"])[3]').click()
  # download as XLS-file
  browser.find_element_by_xpath('//div[@class="b-statistics-form__download-as-xls"]').click()
  #browser.find_element_by_xpath('//div/a/span').click()
  browser.find_element_by_link_text("скачать в виде XLS-файла").click()
  # browser.find_element_by_xpath('//td[6]/table/tbody/tr/td[2]/a').click()

def statistics2db(ya_context):
  global db, cursor

  files = os.listdir(ya_context['download'])
  devnull = open('/dev/null', 'w')
  # convert xls to csv
  for file in files:
    base, ext = file.split('.')
    xlspath = ya_context['download'] + '/' + file
    csvpath = ya_context['download'] + '/' + base + '.csv'
    subprocess.call(["ssconvert", xlspath, csvpath], stdout=devnull, stderr=devnull)
  # remove xls files  
  for file in files:
    os.remove(ya_context['download'] + '/' + file)
  # parse csv files
  stats = os.listdir(ya_context['download'])
  for stat in stats:
    year, month, day, _, _, _ = stat.split('-')
    # get date for statistic
    date = year + '-' + month + '-' + day
    with open(ya_context['download'] + '/' + stat, 'r') as csv_file:
      data = csv.reader(csv_file, delimiter=',')
      keys = []
      values = [] 
    
      for row in data:
        if data.line_num == 2:
          for col in xrange(3, len(row) - 1):
            key = unicode(row[col], "utf-8")
            keys.append(key)
        elif data.line_num == 3:
          for col in xrange(3, len(row) - 1):
            value = unicode(row[col], "utf-8")
            values.append(value) 
         
      for idx in xrange(1, len(keys) - 1):
        str = u"%s\n" % keys[idx]
	print str	  
       
def main():
  global db, cursor
  try:
    opts, args = getopt.getopt(sys.argv[1:], "p:", [ "proxy=", "conf=", "id=", "yesterday", "today" ])
  except getopt.GetoptError as err:
    print str(err)
    usage()
    sys.exit(1)
  
  TIME = None
	
  for o, a in opts:
    if o in ("-p", "--proxy"):
      PROXY = a
    elif o in ("--conf"):
      CONF = a
    elif o in ("--id"):
      ID = a
    elif o in ("--today"):
      TIME = "сегодня"
    elif o in ("--yesterday"):
      TIME = "вчера"
    else:
      assert False, "unhandled option"
   
  # default value 
  if TIME is None:
    TIME = "сегодня"

  config = ConfigParser.RawConfigParser()
  config.read(CONF)
  
  user = config.get('Database', 'user')
  password = config.get('Database', 'password')
  host = config.get('Database', 'host')
  database = config.get('Database', 'database')
  # dir to download stat file 
  download = config.get('Common', 'download')
  # look up database for data
  db = MySQLdb.connect(host=host, user=user, passwd=password, db=database)
  cursor = db.cursor()  
  cursor.execute("SELECT * FROM account WHERE id=" + ID)
  db.commit()
  rows = cursor.fetchall()
  
  ya_context = {}
  ya_context['login'] = rows[0][1]
  ya_context['password'] = rows[0][2] 
  ya_context['resolution_w'], ya_context['resolution_h'] = rows[0][3].split('x')
  ya_context['campaign_name'] = rows[0][4]
  ya_context['user_agent'] = rows[0][5]
  ya_context['proxy'] = PROXY
  ya_context['download'] = download
  ya_context['time'] = TIME
 
  # loging to yandex direct and download a file whith a statistic for today
  autoclick(ya_context)
  statistics2db(ya_context)
  db.close()

if __name__=="__main__":
  main()
