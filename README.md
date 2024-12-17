# ramp-robot
Project 6 Repo

Steps:

1. SSH into Robot A's pi
2. source ~/ramp-robot-venv/bin/activate
3. cd /ramp-robot
4. python3 run.py
5. 

ssh pi@10.243.91.238
cd ramp-robot
git pull origin main
source ~/ramp-robot-venv/bin/activate
python3 left.py OR right.py depending on which ramp


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
