# ramp-robot
Project 6 Repo

Steps:

1. SSH into Robot A's pi
2. source ~/ramp-robot-venv/bin/activate
3. cd /ramp-robot
python3 run.py --side left --ip 10.243.91.238
5. 

ssh pi@10.243.91.238
cd ramp-robot
git pull origin main
source ~/ramp-robot-venv/bin/activate
python3 run.py --side left --ip 10.243.91.238  <change --side and  --ip>


Robot B Steps:
ssh pi@10.243.91.50
cd ramp-robot
git pull origin main
source ~/ramp-robot-venv/bin/activate


Robot A:
    user:   pi@10.243.91.238
    password: -----
    port:   5000

Robot B:
    user:   pi@10.243.91.50
    password: -----
    port:   5000
