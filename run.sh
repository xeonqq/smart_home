docker run  -d --restart always --network=host -v /home/pi/mount:/home/pi/mount \
-v /etc/timezone:/etc/timezone:ro \
-v /etc/localtime:/etc/localtime:ro \
-v $(pwd):/usr/src/app \
-it --name smart_home_app my-python-app
