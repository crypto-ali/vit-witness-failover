#VIT Witness Failover Script

import os
import sys
import json
import datetime
import time
from pprint import pprint
from beem.witness import Witness
from beem import Steem
from beem.instance import set_shared_steem_instance
from beem.transactionbuilder import TransactionBuilder
from beembase import operations
from beem.amount import Amount
from beem.asset import Asset

CUSTOM_CHAINS = json.loads(os.environ.get('CUSTOM_CHAINS', '{}'))
NATIVE_SYMBOL = os.environ.get('NATIVE_SYMBOL', 'VIT')
NATIVE_PREFIX = os.environ.get('NATIVE_PREFIX', 'VIT')
NATIVE_VESTED = os.environ.get('NATIVE_VESTED', 'VESTS')

#Variables:
acct = "username" #put your witness name here
#wif="Active Key Here"
#Number of total blocks missed to deactivate primary witness server.
primary_threshold = 10
#Number of total blocks missed to deactivate backup witness server.
#Note: backup_threshold should always be greater than primary_threshold.
backup_threshold = 20
#Backup server signing key with VIT prefix removed.
backup_signing_key = "YourBackupKeyWithVITprefixRemoved"

stm = Steem(
	node=["https://peer.vit.tube/"],
	bundle=True,
	blocking="head",
	nobroadcast=True, #set True for testing
	custom_chains=CUSTOM_CHAINS,
	#keys={'active': wif},
)

while True:
  try:
    set_shared_steem_instance(stm)
    currentdatetime = datetime.datetime.now()
    w1 = Witness(acct)
    json_string = json.dumps(w1.json(), indent=4)
    data = json.loads(json_string)
    total_missed = data["total_missed"]
    print(currentdatetime.strftime("%a %b %d %Y - %I:%M:%S %p"))
    print("Witness " + acct + " current total missed: " + str(total_missed))
    if total_missed >= primary_threshold:
      print("Total missed at or above threshold. Disabling primary witness server.")
	  #Disable witness.
      tx = TransactionBuilder(steem_instance=stm)
      update_witness = {
        "owner": acct, 
        "url": "No website yet", 
        "block_signing_key": NATIVE_PREFIX + '1111111111111111111111111111111114T1Anm', 
        "props": {
          "account_creation_fee": Amount("0.100 %s" % (NATIVE_SYMBOL)),
          "maximum_block_size":131072, 
        },
      "fee": Amount("0.000 %s" % (NATIVE_SYMBOL)),
      "prefix": NATIVE_PREFIX,
      }
      op = operations.Witness_update(**update_witness)
      tx.appendOps(op)
      tx.appendSigner(acct, "active")
      #tx.appendWif(wif)
      signed_tx = tx.sign()
      broadcast_tx = tx.broadcast()
      pprint(broadcast_tx)
      print("Primary witness server disabled.")
      break
    else:
      print("Primary witness server operational")
      print("----------------------------------")
    time.sleep(60) #Pause script for 60 seconds.
  except KeyboardInterrupt:
    exit()

#Enable backup witness server.
try:
  #Pause script momentarily after disabling primary witness. Recommend minimum 60 seconds.
  time.sleep(60)
  print("Enabling backup witness server.")
  tx = TransactionBuilder(steem_instance=stm)
  update_witness = {
    "owner": acct, 
    "url": "No website yet", 
    "block_signing_key": NATIVE_PREFIX + backup_signing_key, 
    "props": {
      "account_creation_fee": Amount("0.100 %s" % (NATIVE_SYMBOL)),
      "maximum_block_size":131072, 
    },
  "fee": Amount("0.000 %s" % (NATIVE_SYMBOL)),
  "prefix": NATIVE_PREFIX,
  }
  op = operations.Witness_update(**update_witness)
  tx.appendOps(op)
  tx.appendSigner(acct, "active")
  #tx.appendWif(wif)
  signed_tx = tx.sign()
  broadcast_tx = tx.broadcast()
  pprint(broadcast_tx)
  print("Backup witness server enabled. Monitoring of backup server will commence shortly.")
  time.sleep(10) #Seconds you want to wait before you start monitoring the backup server.
except:
  print("Error enabling backup witness.")
  exit()

while True:
  try:
    set_shared_steem_instance(stm)
    currentdatetime = datetime.datetime.now()
    w1 = Witness(acct)
    json_string = json.dumps(w1.json(), indent=4)
    data = json.loads(json_string)
    total_missed = data["total_missed"]
    print(currentdatetime.strftime("%a %b %d %Y - %I:%M:%S %p"))
    print("Witness " + acct + " current total missed: " + str(total_missed))
    if total_missed >= backup_threshold:
      print("Total missed at or above threshold. Disabling backup witness server.")
	  #Disable witness.
      tx = TransactionBuilder(steem_instance=stm)
      update_witness = {
        "owner": acct, 
        "url": "No website yet", 
        "block_signing_key": NATIVE_PREFIX + '1111111111111111111111111111111114T1Anm', 
        "props": {
          "account_creation_fee": Amount("0.100 %s" % (NATIVE_SYMBOL)),
          "maximum_block_size":131072, 
        },
      "fee": Amount("0.000 %s" % (NATIVE_SYMBOL)),
      "prefix": NATIVE_PREFIX,
      }
      op = operations.Witness_update(**update_witness)
      tx.appendOps(op)
      tx.appendSigner(acct, "active")
      #tx.appendWif(wif)
      signed_tx = tx.sign()
      broadcast_tx = tx.broadcast()
      pprint(broadcast_tx)
      print("Backup witness server disabled. Program terminating.")
      exit()
    else:
      print("Backup witness server operational")
      print("---------------------------------")
    time.sleep(60) #Pause script for 60 seconds.
  except KeyboardInterrupt:
    exit()