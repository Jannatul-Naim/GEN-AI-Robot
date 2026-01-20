source /home/naim/venv/bin/activate
cd ~/GEN-AI-Robot
python -m launch.run_vision_stack

source /home/naim/venv/bin/activate
cd ~/GEN-AI-Robot
python -m main


sudo fuser -k /dev/ttyUSB0
