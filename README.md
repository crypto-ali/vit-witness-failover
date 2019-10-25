***DEV BRANCH - WORK IN PROGRESS***

# vit-witness-failover
*VIT Witness Server Kill Switch and Failover*

**Kill Switch:** Automatic kill switch for single witness server.

**Failover:** Automatic failover from primary witness server to backup witness server, with kill switch if backup fails.

Thanks to Simon for helping with the witness enable/disable transaction code for this script.

I built these two scripts to use on my VIT Witness server. The scripts monitor your witness account’s total blocks missed. In the scripts you set a threshold variable that is a number greater than your current total missed blocks. If you miss enough blocks that your account’s total missed blocks number is greater than or equal to your threshold value, then the scripts will take action. I currently use the failover script as I have a backup server. If you have only one server, then you should use the kill switch script.

There are two verisions of each script. The version with a 1 at the end of the file name includes email notification feature.

Lastly, you can choose to run this script on a detatched screen or as a system service. I run it as a system service that starts on system boot. This makes the script more reliable.

### Warning: Use this at your own risk. 
This script requires knowledge of Linux, Python, Beem, and the VIT Blockchain. I make no promises or guarantees with this software. Please see the software license for more information.


**Requirements:**
* Python 3.7
* Beem 0.20.22
* Your VIT Witness account’s active key

**Recommendation:**
* Run this script on a separate server from your witness server(s)

**Setup:**
* Clone or download repo to your Linux machine
* [Install required packages for Beem](https://beem.readthedocs.io/en/latest/installation.html#installation)
* Create a Python virtual environment in the repo’s directory and activate it.
* Install required files: `pip install -r requirements.txt`
* [Create wallet in Beem and set wallet passphrase](https://beem.readthedocs.io/en/latest/cli.html#using-the-wallet)
* [Import your account and add active key into Beem Wallet](https://beem.readthedocs.io/en/latest/cli.html#common-commands)
* Set VIT node in Beem: `beempy set nodes https://peer.vit.tube`

For help with Beem: https://beem.readthedocs.io/en/latest/index.html 


## Version 2.0 Beta

Updates:
* Logging to file
* Run script as a service with auto-restart if sys.exit != 0

Outline of new stuff to document:
* Create .env file
* Set environment variables
* Test with nobroadcast to True
* Setting nobroadcast to False
* Creating the service file 
* Helpful commands for periodic monitoring 


**Configuration:**

Decide if you are going to use the kill switch script or the failover script and follow the corresponding directions below. If you only have one server and not backup, use the kill switch script. If you have a primary witness server and a backup witness server to fail back to, use the failover script.



## OLD SECTION - Remove before merging to Master.

### Kill Switch:

While in the repo directory on your Linux machine run:

```$ cp sample-killswitch.py killswitch.py```

Open killswitch.py with a text editor.

_**Recommended:**_ If using environment variable or keyring to keep Beem wallet unlocked make the following edits:
* Line 23: Replace username with your witness account username
* Line 25: Set threshold to equal the total number of blocks missed for killswitch to activate
* Line31: Set nobroadcast. Set to True for testing or False for production

Save the file.

_**Not recommended:**_ If you will be using your active key directly in the script, make the following edits:
* Line 23: Replace username with your witness account username
* Line 24: Uncomment and add your active key
* Line 25: Set threshold to equal the total number of blocks missed for killswitch to activate.
* Line 31: Set nobroadcast. Set to True for testing or False for production
* Line 33: Uncomment line 33
* Line 63: Comment line 63
* Line 64: Uncomment line 64

Save the file.

#### Test killswitch.py
* Set nobroadcast=True
* Set threshold to a number greater than your current total blocks missed
* Run script
* In console you should see date, time, witness name, total missed and statement: “Witness server operational”. This will update every 60 seconds.
* After confirming proper operation, stop script.
* Set threshold to 0 to test disable script in nobroadcast mode
* Run script
* Console should report that total missed is at or above threshold, disabling server. Then you will see a transaction print.
* If you see this, it worked.

If desired you can also do a live test with nobroadcast set to False and threshold set to 0 to see the kill switch script actually disable the witness. This will ensure that you don’t have any wallet locked, incorrect password, missing key, or any other wallet or active authority related issues.

After successfully disabling witness with the live test procedure, re-enable witness.

Once you confirm that everything is working, set nobroadcast to False, set threshold to some number greater than your current total missed blocks, and save file. 

Then run the script in a screen and detach screen before exiting your session so that the script will continue to run. This is not a set it and forget it tool. You should still regularly check your witness server and monitor server for correct functioning.

### Failover:

While in the repo directory on your Linux machine run:

```$ cp sample-failover.py failover.py```

Open failover.py with a text editor.

_**Recommended:**_ If using environment variable or keyring to keep Beem wallet unlocked make the following edits:
* Line 23: Replace username with your witness account username
* Line 26: Set primary_threshold to equal the total number of blocks missed for failover to activate
* Line 29: Set backup_threshold to equal the total number of blocks missed for kill switch to activate
* Line 31: Set backup_signing_key. Paste you backup witness server block signing key here with the VIT prefix removed. Ex. If your key is: “VIT789abc123xyz”, put “789abc123xyz”.
* Line 37: Set nobroadcast. Set to True for testing or False for production

Save the file.

_**Not recommended:**_ If you will be using your active key directly in the script, make the following edits:
* Line 23: Replace username with your witness account username
* Line 24: Uncomment and paste active key
* Line 26: Set primary_threshold to equal the total number of blocks missed for failover to activate
* Line 29: Set backup_threshold to equal the total number of blocks missed for kill switch to activate
* Line 31: Set backup_signing_key. Paste your backup witness server block signing key here with the VIT prefix removed. Ex. If you key is: “VIT789abc123xyz”, put “789abc123xyz”.
* Line 37: Set nobroadcast. Set to True for testing or False for production
* Line 39: Uncomment line 39
* Line 69: Comment line 69
* Line 70: Uncomment line 70
* Line 102: Comment line 102
* Line 103: Uncomment line 103
* Line 140: Comment line 140
* Line 141: Uncomment line 141

Save the file.

#### Test the failover.py
* Set nobroadcast=True
* Test 1: Set both primary and backup thresholds to a number greater than your current total blocks missed
* Run script
* In console you should see date, time, witness name, total missed and statement: “Primary witness server operational”. This will update every 60 seconds.
* After confirming proper operation, stop script.
* Test 2: Set primary threshold to 0 and backup threshold to a number higher than your current total blocks missed to test primary server disable script in nobroadcast mode
* Run script
* In console you should see “Total missed at or above threshold. Disabling primary witness server.” It will then print a disable transaction and “Primary witness server disabled.” Then 60 seconds later it will show “Enabling backup witness server.” It will then print a witness enable transaction with your backup signing key along with a message that it will begin monitoring backup witness soon. Lastly, you should see date, time, witness name, total missed and statement: “Backup witness server operational”. This will update every 60 seconds.
* After confirming proper operation, stop script.
* Test 3: Final nobroadcast test: Set both thresholds to 0.
* Run script
* In console you should see “Total missed at or above threshold. Disabling primary witness server.” It will then print a disable transaction and “Primary witness server disabled.” Then 60 seconds later it will show “Enabling backup witness server.” It will then print a witness enable transaction with your backup signing key along with a message that it will begin monitoring backup witness soon. Then when monitoring of back up witness starts you should see “Total missed at or above threshold. Disabling backup witness server.” Then it will print a disable witness transaction in console and exit the program.
* If all three tests pass, then the script is working as intended.

If desired you can also do a live test with nobroadcast set to False and both thresholds set to 0 to see the failover script actually disable, enable, and then disable the witness. This will ensure that you don’t have any wallet locked, incorrect password, missing key, or any other wallet or active authority related issues. 

After successfully disabling witness with the live test procedure, re-enable witness.

Once confirmed that everything is working, set nobroadcast to False, set thresholds greater than current total missed (backup_threshold should always be greater than primary_threshold), and save file. 

Then run the script in a screen and detach screen before exiting your session so that the script will continue to run. This is not a set it and forget it tool. You should still regularly check your witness server and monitor server for correct functioning.
