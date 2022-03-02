from lib.utils import *


import re
from lib.db import MongoDB

db = MongoDB(db="Tweettioc")

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


def start():
    count = 0
    wl_ip, wl_dom = loadWhitelist("whitelist.txt")
    domain_data = db.aggregate(collection="tweets", query=[{
            "$match": {"domain": {"$regex": ".+"}}
        },
        {"$project": {
            "_id": 1,
            "domain": 1,
        }},
        ])
    for x in domain_data:
        domains = x['domain'][:]
        changing = 0
        for dom in x['domain']:
            for wl in wl_dom:
                if (wl.match(dom) and dom) in x['domain']:
                    domains.remove(dom)
                    changing=1
                    count +=1
                    print('deleted --> ' + dom)

        if changing:
            myquery = {"_id": x['_id']}
            newvalues = {"$set": {"domain": domains, "url": []}}
            #ioc.update_one(myquery, newvalues)

    #
    # for x in ioc.find({"ip": {"$regex": ".+"}}, {"_id": 1, "ip": 1}):
    #     ioc_ip = x['ip'][:]
    #     changing = 0
    #     for ip in x['ip']:
    #         for wl in wl_ip:
    #             if wl.find('/') >= 0:
    #                 wl_nw = ipaddress.ip_network(wl)
    #                 if ipaddress.ip_address(ip) in wl_nw and ip in ioc_ip:
    #                     ioc_ip.remove(ip)
    #                     changing = 1
    #                     count += 1
    #                     print('deleted --> ' + ip)
    #             else:
    #                 if ip == wl and ip in ioc_ip:
    #                     ioc_ip.remove(ip)
    #                     changing = 1
    #                     count += 1
    #                     print('deleted --> ' + ip)
    #         if changing:
    #             myquery = {"_id": x['_id']}
    #             newvalues = {"$set": {"ip": ioc_ip}}
    #             ioc.update_one(myquery, newvalues)

    print('deleted count --> ' + str(count))


start()