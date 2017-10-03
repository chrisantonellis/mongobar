# debian & python3.6
FROM python:3.6

# set timezone
RUN echo "US/Eastern" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

# add mongodb to sources list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
RUN echo "deb http://repo.mongodb.org/apt/debian jessie/mongodb-org/3.4 main" | tee /etc/apt/sources.list.d/mongodb-org-3.4.list
RUN apt-get update && apt-get -y upgrade

# nano editor
RUN apt-get install nano

# mongodb
RUN apt-get install -y mongodb-org
RUN mkdir -p /data/db

# add mongobar
ADD ./mongobar /mongobar/mongobar
ADD ./setup.py /mongobar/setup.py
ADD ./.mongobar_config.json /root/.mongobar_config.json

# install mongobar
WORKDIR /mongobar
RUN pip install -e .[tests]

# add tests
ADD ./tests /tests

# add init scripts
WORKDIR /

# ADD ./init.sh /init.sh
ADD ./init_auth.sh /init_auth.sh

# RUN chmod 775 /init.sh
RUN chmod 775 /init_auth.sh

# run forevz bby
CMD ["mongod"]
