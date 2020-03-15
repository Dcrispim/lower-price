# install google chrome
FROM python:3.7

RUN apt-get update 
RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils

#download and install chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

#copy local files
COPY . /app 

#install python dependencies
RUN pip install -r /app/requirements.txt &&  echo 'python3 /app/Cli.py $*' >> /bin/lower-price && chmod +x /bin/lower-price && lower-price -tests 



CMD lower-price --reload-simbols && clear && /bin/bash 