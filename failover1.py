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
FROM_PASS = os.getenv('FROM_PASS')
TO = os.getenv('TO_ADDRESS')

yag = yagmail.SMTP(FROM, FROM_PASS)

# Email Alert Variables:
primary_subject = "Primary witness server failed, failover activated"
primary_body = f"Your primary VIT Witness server missed more than your set primary threshold of {P_THRESHOLD} total missed blocks." \
  "The failover script disabled your primary witness server."

failover_subject = "Backup witness server activated"
failover_body = "Your backup VIT Witness server was succesfully activated by the failover script. " \
  f"The killswitch will shut down the backup server if your backup threshold of {B_THRESHOLD} total missed blocks is reached." \

backup_subject = "Backup witness server failed, killswitch activated"
backup_body = f"Your backup VIT Witness server missed more than your set backup threshold of {B_THRESHOLD} total missed blocks." \
  "The failover script activated killswitch and disabled your backup witness server."

exception_subject = "Killswitch script encountered an error and stopped"
exception_body = """Your killswitch script encountered an unhandled exception and has stopped running. 
Please login to your monitoring server to review logs and restart the failover service."""

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
    if total_missed >= P_THRESHOLD:
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
      status_logger.logger.warning("Total missed at or above threshold. Disabling primary witness server. \nOperation: " + json.dumps(broadcast_tx, indent=4))
      yag.send(TO, primary_subject, primary_body)
      break
    else:
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
    yag.send(TO, exception_subject, exception_body)	
    sys.exit()

#Enable backup witness server.
try:
  #Pause script momentarily after disabling primary witness.
  time.sleep(60)
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
  yag.send(TO, failover_subject, failover_body)
  time.sleep(10) #Seconds you want to wait before you start monitoring the backup server.
except Exception as e:
  status_logger.logger.exception("Exception occured\n")
  yag.send(TO, exception_subject, exception_body)
  sys.exit()

while True:
  try:
    set_shared_steem_instance(stm)
    currentdatetime = datetime.datetime.now()
    w1 = Witness(ACCT)
    json_string = json.dumps(w1.json(), indent=4)
    data = json.loads(json_string)
    total_missed = data["total_missed"]
    if total_missed >= B_THRESHOLD:
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
      status_logger.logger.warning("Total missed at or above threshold. Disabling backup witness server. \nOperation: " + json.dumps(broadcast_tx, indent=4))
      yag.send(TO, backup_subject, backup_body)
      sys.exit()
    else:
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
    yag.send(TO, exception_subject, exception_body)
    sys.exit()