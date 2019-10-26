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

### Version 2.0 New Featurs
* Better logging
* Run script as a service with auto-restart if system service exits non-zero
* Script automatically reconnects to VIT node if connection dropped due to temporary network issues

**Requirements:**
* Linux OS - tested mostly with Ubuntu
* Python 3.7 (not tested in 3.8, yet)
* Modules listed in requirements.txt file
* Your VIT Witness account’s active key

**Recommendation:**
* Run this script on a separate server from your witness server(s)

**General Setup:**
* Clone or download repo to your Linux machine
* [Install required packages for Beem](https://beem.readthedocs.io/en/latest/installation.html#installation)
  * ```sudo apt-get install build-essential libssl-dev python-dev curl```
  * For Python3.7 also install: `sudo apt install python3.7-dev`
* Create a Python virtual environment in the repo’s directory and activate it.
* Install required files: `pip install -r requirements.txt`
* Set VIT node in Beem: `beempy set nodes https://peer.vit.tube`
* [Create wallet in Beem and set wallet passphrase](https://beem.readthedocs.io/en/latest/cli.html#using-the-wallet)
  * `beempy createwallet`
* [Import your account and add active key into Beem Wallet](https://beem.readthedocs.io/en/latest/cli.html#common-commands)

For help with Beem: https://beem.readthedocs.io/en/latest/index.html 


### Configuration:

Decide if you are going to use the kill switch script or the failover script. If you only have one server and not backup, use the kill switch script. If you have a primary witness server and a backup witness server to fall back to, use the failover script.

Next, decide if you want to receive email notifications when this monitoring script takes action. If no notifications wanted, run killswitch.py or failover.py. If you do want email notifications, run either killswitch1.py or failover1.py. You will need to add a Gmail address as the from address, its app password as well as a to address in the .env file to receive notifications.

Lastly, decide if you want to run this script on a detatched screen or as a system service. Running as a detatched screen is easier. Running as a system service allows it to run in the background as well as have the ability to enable the service to start when the VPS boots up or is rebooted after installing updates, etc.

If you run script in a detatched screen all logs will be written to status.log file in the script's directory. If running as a system service all logs are written to the system journal.

**Create .env file**

Run: 

```$ cp sample.env.txt .env```

Open .env file in your preferred text editor and fill out or set all variables and save file. If you are running one of the killswitch scripts you will need to only adjust the K_THRESHOLD variable for missed blocks. If running one of the failover scripts you will need to set P_THRESHOLD and B_THRESHOLD variables for total missed blocks for both primary and backup witness servers. Also, if using email notifications, fill in the three Yagmail variables at the bottom of the file.

When using the email notifications you must use a Gmail address for the from address. For security it is recommended to us an app password instead of your Gmail account's regular password. For information on using app passwords, [see this Google Support article](https://support.google.com/accounts/answer/185833?hl=en).

### Testing

Open a new screen:

```$ screen```

Navigate to the script's directory if you aren't already in it. Activate your virtual environment.

```$ source venv/bin/activate```

Replace venv with whatever you named your virtual environment.

**Testing Email Sending**

If you are using email notifications: open .env file with your preferred text editor, set LOG_LEVEL=INFO, add your three Yagmail variables, and save. Then run:

```$ python yagmail-setup.py```

If no errors, console will report email is successfully sent. Check your TO email address's inbox. It may take a few minutes to arrive. Any errors will print to console and be written to status.log. 

**Test witness update operations with nobroadcast set to True**

Open your .env file with your preferred text editor and set NO_BROADCAST=1. Set LOG_LEVEL=INFO to see detailed info printed to console and written to status.log. 

**First test:** 
Set your threshold variable(s) higher than your total missed and save the .env file.

Now run your chosen script, ex:

```$ python killswitch.py```

Console should print info about your witness and current total missed and that server is operational. If so, test is successful.

**Second test:**
Set your K_THRESHOLD variable below your total missed or to 0 to test. If running failover script, set P_THRESHOLD variable below or to 0.

Run your chosen script.

Console should report warning about missing too many blocks and deactivating. If killswitch script, script will exit after running disable witness operation. If failover script, it will disable primary witness, wait for one minute, activate backup, then begin monitoring backup witness. If this is what happens, test passed.

**Test three (failover script only):**
Set both thresholds to below your total missed or to 0 to test.

Run your chosen script.

Console should report warning about missing too many blocks and deactivate primary witness. After one minute it will activate backup witness. After about 10 seconds it will begin monitoring backup witness and see it too has missed too many blocks and will deactivate backup. If this is what happens, test passed.

Once you have passed all tests your script is ready to be put into production. If you want to be doubly sure that your script is functioning properly, carry out all the tests again with NO_BROADCAST=0 to do live witness updates. This is the absolute way to ensure that you have no wallet or key permission errors that would keep the script from updating your witness.

### Run in Production

Now that you are ready to run the script in production, open your .env file with your preferred text editor. Set NO_BROADCAST=0. Set LOG_LEVEL=WARNING. Set your threshold variable(s) to higher than your total missed. Save the file.

**Running in detatched screen**

Open a new screen:

```$ screen```

Navigate to the script's directory if you aren't already in it. Activate your virtual environment.

```$ source venv/bin/activate```

Replace venv with whatever you named your virtual environment.

Now run your chosen script, ex:

```$ python killswitch.py```

Since you are now running it with LOG_LEVEL=WARNING, you won't see anything printed to the console as long as everything is working correctly. Only warnings and errors will be logged.

To detatch screen, type:

```Ctrl-a d```

Now you can exit your SSH session on your VPS and log back in later. 

For more info on using screen, see the [screen man page](https://linux.die.net/man/1/screen).

**Running as a system service**

To run the script as a system service it is necessary to create a service file.

Step 1: Change to /lib/systemd/system directory. 

Step 2: Create and open a new .service file using your preferred text editor. Give the file a memorable name. Ex:

```$ sudo vi vitwitness.service```

or

```$ sudo nano vitwitness.service```

Now paste in the contents of sample-service-file.txt from the Github repo. Text is included below for convenience.

```
[Unit]
Description=VIT Witness Failover and Killswitch
After=multi-user.target

[Service]
Type=simple
ExecStart=/path/to/ENV/bin/python /path/to/python/script.py
Restart=on-failure
RestartSec=30s

[Install]
WantedBy=multi-user.target
``` 

Now, edit the ExecStart line. You need to replace the two file paths. The first path is the path to the Python executable in your virtual environment. The second path is the path to the witness script you want to run (killswitch.py, failover1.py, etc).

If you cloned the repo on an Ubuntu machine in the user directory then your ExecStart line would look something like this:

```ExecStart=/home/USERNAME/vit-witness-failover/venv/bin/python /home/USERNAME/vit-witness-failover/SCRIPT.py```

Replacing USERNAME with your Linux VPS username and replacing SCRIPT with the witness monitor script your want to use (killswitch.py, failover1.py, etc).

Save the file.

Then run:

```$ sudo systemctl daemon-reload```

To set the service to autostart on system boot, run:

```$ sudo systemctl enable vitwitness.service```

To start the service, run:

```$ sudo systemctl start vitwitness.service```

To check the status of the service, run:

```$ sudo systemctl status vitwitness.service```

In the commands above, change vitwitness.service to whatever you named your service file. If you make changes to your service file, after saving them remember to run the daemon-reload command above to make your file changes get picked up by systemd.

Common systemctl commands:

```$ sudo systemctl start vitwitness.service```

```$ sudo systemctl stop vitwitness.service```

```$ sudo systemctl restart vitwitness.service```

```$ sudo systemctl status vitwitness.service```

Disable autostart on system boot: `$ sudo systemctl disable vitwitness.service`

For more information on using systemctl, see the [systemctl man page](http://manpages.ubuntu.com/manpages/xenial/man1/systemctl.1.html).

Lastly, to check on your witness killswitch / failover script running as a service, you can use the following two commands:

```$ sudo systemctl status vitwitness.service```

```$ sudo journalctl --unit=vitwitness.service```


*This is not a set it and forget it tool. You should still regularly check your witness server and monitor server for correct functioning.*
