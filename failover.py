#VIT Witness Failover

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
from dotenv import load_dotenv
import yagmail

import status_logger

load_dotenv()

#Variables:
CUSTOM_CHAINS = json.loads(os.environ.get('CUSTOM_CHAINS', '{}'))
NATIVE_SYMBOL = os.environ.get('NATIVE_SYMBOL', 'VIT')
NATIVE_PREFIX = os.environ.get('NATIVE_PREFIX', 'VIT')
NATIVE_VESTED = os.environ.get('NATIVE_VESTED', 'VESTS')
ACCT = os.getenv('ACCOUNT')
NO_BROADCAST = os.getenv('NO_BROADCAST')
P_THRESHOLD = int(os.getenv('P_THRESHOLD'))
B_THRESHOLD = int(os.getenv('B_THRESHOLD'))
BACKUP_KEY = os.getenv('BACKUP_KEY')
WIF = os.getenv('WIF')
FROM = os.getenv('FROM_ADDRESS')
TO = os.getenv('TO_ADDRESS')

stm = Steem(
	node=["https://peer.vit.tube/"],
	bundle=True,
	blocking="head",
	nobroadcast=NO_BROADCAST, #set True for testing
	custom_chains=CUSTOM_CHAINS,
	keys={'active': WIF},
)

while True:
  try:
    set_shared_steem_instance(stm)
    currentdatetime = datetime.datetime.now()
    w1 = Witness(ACCT)
    json_string = json.dumps(w1.json(), indent=4)
    data = json.loads(json_string)
    total_missed = data["total_missed"]
    #print(currentdatetime.strftime("%a %b %d %Y - %I:%M:%S %p"))
    #print("Witness " + ACCT + " current total missed: " + str(total_missed))
    if total_missed >= P_THRESHOLD:
      #print("Total missed at or above threshold. Disabling primary witness server.")
	  #Disable witness.
      tx = TransactionBuilder(steem_instance=stm)
      update_witness = {
        "owner": ACCT, 
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
      #tx.appendSigner(ACCT, "active")
      tx.appendWif(WIF)
      signed_tx = tx.sign()
      broadcast_tx = tx.broadcast()
      #pprint(broadcast_tx)
      #print("Primary witness server disabled.")
      status_logger.logger.warning("Total missed at or above threshold. Disabling primary witness server. \nOperation: " + json.dumps(broadcast_tx, indent=4))
      break
    else:
      #print("Primary witness server operational")
      #print("----------------------------------")
      status_logger.logger.info("Witness " + ACCT + " current total missed: " + str(total_missed) + "\nPrimary witness server operational\n--------------------------")
    time.sleep(60) #Pause script for 60 seconds.
  except KeyboardInterrupt:
    sys.exit()
  except Exception as WitnessDoesNotExistsException:
    status_logger.logger.exception("Exception occured\n")
    status_logger.logger.info("Reconnecting...")
    stm = Steem(
      node=["https://peer.vit.tube/"],
      bundle=True,
      blocking="head",
      nobroadcast=NO_BROADCAST, #set True for testing	
      custom_chains=CUSTOM_CHAINS,
	  keys={'active': WIF},
    )
  except Exception as e:
    status_logger.logger.exception("Exception occured\n")
    sys.exit()

#Enable backup witness server.
try:
  #Pause script momentarily after disabling primary witness.
  time.sleep(60)
  #print("Enabling backup witness server.")
  tx = TransactionBuilder(steem_instance=stm)
  update_witness = {
    "owner": ACCT, 
    "url": "No website yet", 
    "block_signing_key": NATIVE_PREFIX + BACKUP_KEY, 
    "props": {
      "account_creation_fee": Amount("0.100 %s" % (NATIVE_SYMBOL)),
      "maximum_block_size":131072, 
    },
  "fee": Amount("0.000 %s" % (NATIVE_SYMBOL)),
  "prefix": NATIVE_PREFIX,
  }
  op = operations.Witness_update(**update_witness)
  tx.appendOps(op)
  #tx.appendSigner(ACCT, "active")
  tx.appendWif(WIF)
  signed_tx = tx.sign()
  broadcast_tx = tx.broadcast()
  #pprint(broadcast_tx)
  #print("Backup witness server enabled. Monitoring of backup server will commence shortly.")
  time.sleep(10) #Seconds you want to wait before you start monitoring the backup server.
except Exception as e:
  status_logger.logger.exception("Exception occured\n")
  sys.exit()

while True:
  try:
    set_shared_steem_instance(stm)
    currentdatetime = datetime.datetime.now()
    w1 = Witness(ACCT)
    json_string = json.dumps(w1.json(), indent=4)
    data = json.loads(json_string)
    total_missed = data["total_missed"]
    #print(currentdatetime.strftime("%a %b %d %Y - %I:%M:%S %p"))
    #print("Witness " + ACCT + " current total missed: " + str(total_missed))
    if total_missed >= B_THRESHOLD:
      #print("Total missed at or above threshold. Disabling backup witness server.")
	  #Disable witness.
      tx = TransactionBuilder(steem_instance=stm)
      update_witness = {
        "owner": ACCT, 
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
      #tx.appendSigner(ACCT, "active")
      tx.appendWif(WIF)
      signed_tx = tx.sign()
      broadcast_tx = tx.broadcast()
      #pprint(broadcast_tx)
      #print("Backup witness server disabled. Program terminating.")
      status_logger.logger.warning("Total missed at or above threshold. Disabling backup witness server. \nOperation: " + json.dumps(broadcast_tx, indent=4))
      sys.exit()
    else:
      #print("Backup witness server operational")
      #print("---------------------------------")
      status_logger.logger.info("Witness " + ACCT + " current total missed: " + str(total_missed) + "\nBackup witness server operational\n--------------------------")
    time.sleep(60) #Pause script for 60 seconds.
  except KeyboardInterrupt:
    sys.exit()
  except Exception as WitnessDoesNotExistsException:
    status_logger.logger.exception("Exception occured\n")
    status_logger.logger.info("Reconnecting...")
    stm = Steem(
      node=["https://peer.vit.tube/"],
      bundle=True,
      blocking="head",
      nobroadcast=NO_BROADCAST, #set True for testing	
      custom_chains=CUSTOM_CHAINS,
	  keys={'active': WIF},
    )
  except Exception as e:
    status_logger.logger.exception("Exception occured\n")
    sys.exit()