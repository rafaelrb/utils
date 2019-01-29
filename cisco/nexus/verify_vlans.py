#!/usr/bin/env python3
import re
import os
import sys
from pprint import pprint
import paramiko

def parse_interfaces(file):
  fd = open(file)
  lines = fd.readlines()
  fd.close()
  interface = None
  interface_old = None
  description = None
  dados = {}

  for line in lines:
    line = line.replace('\n','')
    if re.match('^interface.*',line):
      interface = line.split()[1]
      if interface_old == None:
        interface_old = interface

    if re.match('.*description.*',line):
      description = re.split('.+description ',line)[-1:][0]

    if interface != interface_old:
      dados[interface.replace('port-channel','Po').replace('Ethernet','Eth')] = {'description': description}
  return dados

def parse_vlans(file):
  fd = open(file)
  lines = fd.readlines()
  fd.close()
  vlan = None
  vlan_old = None
  dados = {}
  interfaces = []
  description = None
  description_old = None
  switch = None

  for line in lines:
    line = line.replace('\n','')
    if re.match('.*(enet|isolated).*',line):
      continue

    if re.match('^NXS5K.*',line):
      switch = line.split()[0].replace('#','')

    if re.match('^[0-9]+.*',line):
      vlan = int(line.split()[0])
      description = line.split()[1]
      if vlan_old == None:
        vlan_old = vlan
        description_old = description

    if vlan != vlan_old:
      dados[vlan_old] = {'switch': switch, 'description': description_old, 'interfaces': interfaces }
      interfaces = []
      vlan_old = vlan
      description_old = description

    if re.match('.*(Eth|Po)[0-9]+.*',line):
      item = line[48:]
      for i in item.split():
        if re.match('(Eth10[3-9]|Po[0-9]+)',i):
          interfaces.append(i.replace(',',''))


  return dados

def verify_vlan():

  nxs5k01_interfaces = parse_interfaces('NXS5K01-CORE-CAS-config.txt')
  nxs5k02_interfaces = parse_interfaces('NXS5K02-CORE-CAS-config.txt')
  nxs5k01 =parse_vlans('NXS5K01-CORE-CAS-vlans.txt')
  nxs5k02 =parse_vlans('NXS5K02-CORE-CAS-vlans.txt')
  for k,v in nxs5k01.items():
    if k in nxs5k02.keys():
      for i in v['interfaces']:
        if not i in nxs5k02[k]['interfaces']:
          interface = nxs5k02_interfaces[i]
          print('interface %s (%s) nao possui a vlan %s (%s) no switch %s' % (i, interface['description'] ,k,v['description'],nxs5k02[k]['switch']))
    else:
      print('vlan %s (%s) so existe no switch %s' % (k, v['description'], v['switch']) )

def main():
#  d = parse_interfaces('NXS5K01-CORE-CAS-config.txt')
#  for k,v in d.items():
#    print(k,v['description'])
  verify_vlan()

if __name__ == "__main__":
  main()

