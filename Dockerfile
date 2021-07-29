# Operating system
FROM ubuntu

# Updating system and installing the required packages
RUN apt-get update
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install python3 python3-pip pipenv python3.9 -y

# Copying the source code to the container
COPY . /etc/erin

# changing directories to the source code and running the pipenv install command command
RUN echo "export LANG=en_US.UTF-8" >> ~/.profile
RUN cd /etc/erin;pipenv install --ignore-pipfile

CMD ["pipenv run python3", "/etc/erin/src/main.py"]
