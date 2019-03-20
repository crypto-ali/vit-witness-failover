#VIT Witness Kill Switch

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
threshold = 10 #Number of total blocks missed to activate killswitch.

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
    if total_missed >= threshold:
      print("Total missed at or above threshold. Disabling witness server.")
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
      exit()
    else:
      print("Witness server operational")
      print("--------------------------")
    time.sleep(60) #Pause script for 60 seconds.
  except KeyboardInterrupt:
    exit()