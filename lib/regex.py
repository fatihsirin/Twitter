import re


def getIoCPattern():
  md5_patt = r'\b(?!^[\d]*$)(?!^[a-fA-F]*$)([a-f\d]{32}|[A-F\d]{32})\b'
  sha1_patt = r'\b(?!^[\d]*$)(?!^[a-fA-F]*$)([a-f\d]{40}|[A-F\d]{40})\b'
  sha256_patt = r'\b(?!^[\d]*$)(?!^[a-fA-F]*$)([a-f\d]{64}|[A-F\d]{64})\b'
  ip_patt = r'\b(([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\.)){3}([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\b'
  domain_patt = r'\b((([a-z0-9][a-z0-9\-]{0,61})(\.))+[a-z]{2,}|(([A-Z0-9][A-Z0-9\-]{0,61})(\.))+[A-Z]{2,})\b'
  url_patt = r'\b([a-zA-Z]*(://|//))?(((([a-z0-9][a-z0-9\-]{0,61})(\.))+[a-z]{2,}|(([A-Z0-9][A-Z0-9\-]{0,61})(\.))+[A-Z]{2,}(:[0-9]{1,5})?)|((([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\.)){3}([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(:[0-9]{1,5})?))(/[\w/:%#$&?()~.=+\-\[\]]*)?\b'
  refer_url_patt = r'(https?)://((([A-Za-z0-9][A-Za-z0-9\-]{0,61})\.)+[A-Za-z]+)/([\w/:%#$&?()~.=+\-]*)?'
  mail_addr_patt = r'\b[a-zA-Z0-9.!#$%&\'*+\/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+\b'
  #mail_addr_patt = r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'

  pattern = {}
  pattern['md5'] = re.compile(md5_patt)
  pattern['sha1'] = re.compile(sha1_patt)
  pattern['sha256'] = re.compile(sha256_patt)
  pattern['ip'] = re.compile(ip_patt)
  pattern['domain'] = re.compile(domain_patt)
  pattern['url'] = re.compile(url_patt)
  pattern['mail'] = re.compile(mail_addr_patt,re.MULTILINE)
  pattern['reference'] = re.compile(refer_url_patt)

  return pattern

def loadWhitelist(filename):
  wl_file = open(filename, 'r')
  wl_ip_patt = re.compile(r'(([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\.)){3}([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([1-9]|[1-2][0-9]|3[0-2]))?')
  wl_ip = []
  wl_dom = []
  for line in wl_file.readlines():
    line = line.strip()
    if line != '':
      if line[0] == '#':
        continue
      if wl_ip_patt.match(line):
        wl_ip.append(line)
      else:
        try:
          wl_dom.append(re.compile(line, re.IGNORECASE))
        except:
          print('[-] Whitelist Regular Expression is wrong.')
          print('[-] Confirm Your String: ' + line)
  return wl_ip, wl_dom