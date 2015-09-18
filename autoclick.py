#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import random
import time
import csv
import codecs
import subprocess
import ConfigParser

from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

def usage():	
  print "%s -p addr:port | --proxy addr:port" % os.path.basename(sys.argv[0])

def autoclick(proxy, downloaddir, username, password):
  url_auth = "https://passport.yandex.ru/auth"
  url_direct = "https://direct.yandex.ru/registered/main.pl?cmd=showCamps"

  proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': proxy,
    'ftpProxy': proxy,
    'sslProxy': proxy,
    'noProxy' : ''
  })

  stream_type = "application/octet-stream;application/csv;text/csv;application/vnd.ms-excel;"
  profile = webdriver.FirefoxProfile()
  # set custom location
  profile.set_preference('browser.download.folderList', 2)
  profile.set_preference('browser.download.manager.showWhenStarting', False)
  profile.set_preference('browser.download.dir', downloaddir)
  profile.set_preference('browser.helperApps.neverAsk.saveToDisk', stream_type)
  profile.set_preference("browser.cache.disk.enable", False);
  profile.set_preference("browser.cache.memory.enable", False);
  profile.set_preference("browser.cache.offline.enable", False);
  profile.set_preference("network.http.use-cache", False);
  
  browser = webdriver.Firefox(proxy=proxy, firefox_profile=profile)
  browser.set_window_size(1366, 768)
  browser.get(url_auth)
  # find authentication form
  html_login  = browser.find_element_by_xpath("//input[@id='login']")
  html_passwd = browser.find_element_by_xpath("//input[@id='passwd']")
  html_submit = browser.find_element_by_xpath("//button[@type='submit']")
  # send credentials 
  html_login.clear()
  html_login.send_keys(username)
  html_passwd.clear()
  html_passwd.send_keys(password)
  html_submit.click()
  # jump to the page with campaigns
  browser.get(url_direct)
  # jump to the page with the statistic
  html_stat = browser.find_element_by_link_text('Статистика')
  html_stat.click()
  # download statistic info
  browser.find_element_by_xpath('//span[text() = "сегодня"]').click()
  browser.find_element_by_xpath('(//button[@type="button"])[3]').click()
  # do not understand how it works
  browser.find_element_by_xpath('//div[@class="b-statistics-form__download-as-xls"]').click()
  browser.find_element_by_link_text('скачать в виде XLS-файла').click()
  browser.find_element_by_link_text('Выход').click()
  browser.quit()

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "p:", ["proxy=", "conf=", "dir="])
  except getopt.GetoptError as err:
    print str(err)
    usage()
    sys.exit(1)
	
  for o, a in opts:
    if o in ("-p", "--proxy"):
      PROXY = a
    elif o in ("--conf"):
      CONF = a
    elif o in ("--dir"):
      DOWNLOADDIR = a 
    else:
      assert False, "unhandled option"

  config = ConfigParser.RawConfigParser()
  config.read(CONF)
  
  username = config.get('Credentials', 'username')
  password = config.get('Credentials', 'password')
  # loging to yandex direct and download a file whith a statistic for today
  autoclick(PROXY, DOWNLOADDIR, username, password)
  # now convert this file from xls to csv
  files = os.listdir(DOWNLOADDIR)
  xlsname, _ = os.path.splitext(files[0])
  xlspath = DOWNLOADDIR + "/" + files[0]
  csvpath = DOWNLOADDIR + "/" + xlsname + ".csv"
  txtpath = DOWNLOADDIR + "/" + xlsname + ".txt"
  # run util to convert xls to csv
  subprocess.call(["ssconvert", xlspath, csvpath])

  for file in os.listdir(DOWNLOADDIR):
    if file.endswith(".csv"):
      csv_path = DOWNLOADDIR + "/" + file
      with open(csv_path, 'r') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        keys = []
	values = []
	for row in csv_data:
          if csv_data.line_num == 2:
            for col in xrange(3, len(row) - 1):
              key = unicode(row[col], "utf-8")
              keys.append(key)
          elif csv_data.line_num == 3:
            for col in xrange(3, len(row) - 1):
              value = unicode(row[col], "utf-8")
              values.append(value)
    
        fd = codecs.open(txtpath, "w", "utf-8")
  
        for idx in xrange(1, len(keys) - 1):
          str = u"%s -- (%s)\n" % (keys[idx], values[idx])
          fd.write(str)
   
        fd.close()

  for file in os.listdir(DOWNLOADDIR):
    if file.endswith(".txt"):
      pass
    else:
      os.remove(DOWNLOADDIR + "/" + file) 
  
if __name__ == "__main__":
  main()
