source /home/naim/venv/bin/activate
cd ~/GEN-AI-Robot
python -m launch.run_vision_stack




source ~/venv/bin/activate
groups
ls -l /dev/ttyUSB0
sudo chmod a+rw /dev/ttyUSB0


sudo lsof /dev/ttyUSB0
sudo fuser -v /dev/ttyUSB0


sudo kill -9 PID


sudo lsof /dev/ttyUSB0

sudo systemctl stop ModemManager
sudo systemctl disable ModemManager


systemctl status ModemManager

sudo fuser -k /dev/ttyUSB0
