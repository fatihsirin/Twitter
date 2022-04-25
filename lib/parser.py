from lib.regex import *
import ipaddress
import os
from lib.domain import Domain

wl_mail = open(os.getcwd() + "/mail.txt", 'r')
wl_mail = wl_mail.readlines()

wl_ip = []
wl_dom = []
path_whitelist = os.getcwd() + "/whitelist.txt"
if os.path.exists(path_whitelist):
  (wl_ip, wl_dom) = loadWhitelist(path_whitelist)
elif os.path.exists(os.path.dirname(__file__) +'../whitelist'): #windows çalıştırmasından kaynaklı hatadan eklendi
  (wl_ip, wl_dom) = loadWhitelist(os.path.dirname(__file__) +'../whitelist.txt')
else:
  print('whitelist file couldnt find')
  exit()

def extract(data, patt):
  result = []
  while True:
    m = patt.search(data)
    if not m:
        break
    ioc = m.group()
    if not ioc in result:
      result.append(m.group())
    data = data[m.end():]
  return result

def extractIoC(data, pattern):

  ioc_result = {}
  ioc_result['reference'] = extract(data, pattern['reference'])
  ioc_result['md5'] = extract(data, pattern['md5'])
  ioc_result['sha1'] = extract(data, pattern['sha1'])
  ioc_result['sha256'] = extract(data, pattern['sha256'])

  # data = pattern['reference'].sub(' ', data)
  data = re.sub(r'pic\.twitter\.com\/[a-zA-Z0-9]+', ' ', data)

  dot_patt = r'\s\\\.|\\\.|\[\.\]|\[\.|\.\]|\(\.\)|\(\.|\.\)|\s\[\.\]|\s\[\.|\s\.\]|\s\(\.\)|\s\(\.|\s\.\)|\(dot\)'
  colon_patt = r'\[:\]|:\]|\[:'
  data = re.sub(dot_patt, '.', data)
  data = re.sub(colon_patt, '://', data)

  ioc_result['mail'] = extract(data, pattern['mail'])
  if ioc_result['mail']:
    for i in ioc_result['mail']:
      if not re.match(re.compile(r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"), i):
        ioc_result['mail'].remove(i)

  #data = pattern['mail'].sub(' ', data)
  ioc_result['ip'] = extract(data, pattern['ip'])
  ioc_result['domain'] = extract(data, pattern['domain'])
  ioc_result['url'] = extract(data, pattern['url'])


  ioc_ip = ioc_result['ip'][:]
  for ip in ioc_result['ip']:
    for wl in wl_ip:
      if wl.find('/') >= 0:
        wl_nw = ipaddress.ip_network(wl)
        if ipaddress.ip_address(ip) in wl_nw and ip in ioc_ip:
          ioc_ip.remove(ip)
      else:
        if ip == wl and ip in ioc_ip:
          ioc_ip.remove(ip)
    if ip in ioc_result['url']:
      ioc_result['url'].remove(ip)
  ioc_result['ip'] = ioc_ip

  ioc_domain = ioc_result['domain'][:]
  for domain in ioc_result['domain']:
    isdomain = True
    for url in ioc_result['url']:
      d_pos = url.find(domain)
      if url == domain:
        ioc_result['url'].remove(domain)
      if d_pos > 0:
        tmp = url[:d_pos]
        if tmp.find('.') >= 0:
          if isdomain:
            ioc_domain.remove(domain)
          isdomain = False
    if isdomain:
      for wl in wl_dom:
        if wl.match(domain) and domain in ioc_domain:
          ioc_domain.remove(domain)
  ioc_result['domain'] = ioc_domain



  http_patt = [
    re.compile('^h(x|X)+p://[0-9a-zA-Z].*'),
    re.compile('^://[0-9a-zA-Z].*'),
    re.compile('^/{1,2}[0-9a-zA-Z].*'),
    re.compile('^(p://)')
  ]
  https_patt = [
    re.compile('^h(x|X)+ps://[0-9a-zA-Z].*'),
    # re.compile('^s://[0-9a-zA-Z].*'),
    re.compile('^s/[0-9a-zA-Z].*'),
    re.compile('^(s://)')
  ]
  ioc_url = ioc_result['url'][:]
  for url in ioc_result['url']:
    for patt in http_patt:
      if patt.match(url):
        ioc_url[ioc_url.index(url)] = re.compile('^(h(x|X)+p://|://|/{1,2})|(p://)').sub('http://', url)
        # ioc_url[ioc_url.index(url)] = re.compile('^(p://|://|/{1,2})').sub('http://', url)
    for patt in https_patt:
      if patt.match(url):
        ioc_url[ioc_url.index(url)] = re.compile('^(h(x|X)+ps://|://|/{1,2})|(s://)').sub('https://', url)
        # ioc_url[ioc_url.index(url)] = re.compile('^(ps://|://|/{1,2})').sub('https://', url)
    for wl in wl_dom:
      if wl.match(url) and url in ioc_url:
        ioc_url.remove(url)
        break

  ioc_result['reference'] = list(set([item.lower() for item in ioc_result['reference']]))
  ioc_result['domain'] = list(set([item.lower() for item in ioc_result['domain']]))
  ioc_result['url'] = list(set([item.lower() for item in ioc_result['url']]))


  for i in ioc_url:
    if i.lower() in ioc_result['reference']:
      ioc_result['reference'].remove(i.lower())
  ioc_result['url'] = list(set(ioc_url))

  for i in ioc_result['reference']:
    if "w3.org" in i:
      ioc_result['reference'].remove(i)

  _tmp=ioc_result['domain'][:]
  for name in _tmp:
    valid = Domain(name).valid
    if not valid:
      ioc_result['domain'].remove(name)
      if name in ioc_result['url']:
        ioc_result['url'].remove(name)

  _tmp = ioc_result['mail'][:]
  for name in _tmp:
    valid = Domain(name.split('@')[1]).valid
    if name in wl_mail:
      valid = False
    if not valid:
      ioc_result['mail'].remove(name)

#wl_mail




  return ioc_result
