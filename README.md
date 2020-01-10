```shell
sudo apt install docker.io
sudo groupadd docker
sudo gpasswd -a $USER docker
newgrp docker
docker run hello-world
```

( https://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo )

```shell
docker build --rm -f Dockerfile -t mytensorflow .
docker run --name=MyTensorFlow -p 8888:8888 -v ~/Jupyter/work:/home/jovyan/work -e USER=$USER  -e USERID=$UID  mytensorflow:latest 
```

```shell
docker container ls -a
docker container rm <containername>
```
