source /home/naim/venv/bin/activate
cd ~/GEN-AI-Robot
python -m launch.run_vision_stack



sudo systemctl stop ModemManager
sudo systemctl disable ModemManager


systemctl status ModemManager

sudo fuser -k /dev/ttyUSB0
