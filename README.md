# aws-nxp-ai-at-the-edge

Collaborative demo with Amazon and NXP to plug the pasta demo to AWS services such as AWS IoT Greengrass and AWS SageMaker Neo.

# How to Run on TorizonCore

Prerequisites:

- An AWS account
- On AWS create an AWS IoT service
- On AWS console access AWS IoT
	- Create a new Greengrass group
	- Choose *Use easy creation* on *Set up your Greengrass Group*
	- Choose a name to the group
	- Run scripted configuration
	- Download the certificates for the group

		**WARNING** On the end of the group creation make sure you have
		downloaded and saved the certificates for *Core’s security resources* to
		use on device

		More info about this step: https://docs.aws.amazon.com/greengrass/latest/developerguide/gg-config.html?shortFooter=true

- Add a Lambda function to be deployed on the group
	- Inside the group choose the *Lambdas* item and click "Add Lambda"
	- Create a new Lambda: https://docs.aws.amazon.com/greengrass/latest/developerguide/create-lambda.html?shortFooter=true
	- Configure the new Lambda and add a subscription between the Lambda and
	the AWS IoT service for our Greengrass group https://docs.aws.amazon.com/greengrass/latest/developerguide/config-lambda.html?shortFooter=true

- On the group choose *Deployments* TODO

Configure IoT Greengrass Device:

**WARNING** Make the follow steps on the Toradex device 

- First install the Torizon Core with Docker Runtime with Easy Installer.

	**WARNING:** Use the releases with Kernel 5.0 for iMX6 and 4.14 for iMX8.
	New BSP with kernel 5.2 are with issues on overlayfs

- On the TorizonCore add the user and group:

```
sudo adduser --system ggc_user
sudo addgroup --system ggc_group
sudo reboot
```

- Check if the *hardlinks* and *symlinks* are configured (these parameters must
return =1):

```
sudo sysctl -a 2> /dev/null | grep fs.protected
password:
fs.protected_fifos = 1
fs.protected_hardlinks = 1
fs.protected_regular = 1
fs.protected_symlinks = 1
```

- Configure the *cgroup_memory=1* and *cgroup_enable=memory* on the *cmdline*:

```
cd /boot/loader
sudo su
echo "$(cat uEnv.txt) cgroup_enable=memory cgroup_memory=1" > uEnv.txt
reboot now
```

- Download and run the Greengrass dependency checker:

```
mkdir Downloads
cd Downloads
wget https://github.com/aws-samples/aws-greengrass-samples/raw/master/greengrass-dependency-checker-GGCv1.9.x.zip
unzip greengrass-dependency-checker-GGCv1.9.x.zip
cd greengrass-dependency-checker-GGCv1.9.x
sudo modprobe configs
sudo ./check_ggc_dependencies | more
```

**WARNING** The not found for: Python 2.7, Node.js, Java 8 are normal returns

**WARNING** Make the follow steps on the development enviroment computer where
you made the AWS IoT group configs

- Download the Greengrass runtime software for your device arch:
	- Download @ https://docs.aws.amazon.com/greengrass/latest/developerguide/what-is-gg.html?shortFooter=true#gg-core-download-tab

- Copy the *Core’s security resources* and the *Greengrass runtime software* for
the device 

```
scp greengrass-linux-armv7l-1.9.2.tar.gz torizon@$BOARD_IP:/home/torizon/Downloads
scp 65573b2e8f-setup.tar.gz torizon@$BOARD_IP:/home/torizon/Downloads
```

**WARNING** Go back to device shell to make follow steps

- On device unpack the *Core’s security resources* and the *Greengrass runtime software*

```
cd ~/Downloads
sudo tar -xzvf greengrass-linux-armv7l-1.9.2.tar.gz -C /
sudo tar -xzvf 65573b2e8f-setup.tar.gz -C /greengrass
```

- Download the AWS cert:

```
cd /greengrass/certs/
sudo wget -O root.ca.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem
```

- Start Greengrass Daemon:

```
cd /greengrass/ggc/core/
sudo ./greengrassd start
```

# Troubleshoot

- Check if the Greengrass daemon is running:

```
ps aux | grep -E 'greengrass.*daemon'
```

- Check *runtime.log*

```
sudo su
cd /greengrass/ggc/var/log/system
cat runtime.log
```

- Check Lambda logs

```
cd /greengrass/ggc/var/log/user/us-west-2/227195268013
cat RestGreenGrass_imx8.log
```
