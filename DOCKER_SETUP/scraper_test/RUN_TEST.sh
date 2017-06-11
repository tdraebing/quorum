#!/bin/bash

pushd . 
basedir=`pwd`

cd ../
bash install_docker.sh |& tee INSTALL_DOCKER.txt

cd ../Dockerfiles
sudo docker build -t ubuntu_miniconda -f Dockerfile_miniconda . |& tee MINICONDA_IMAGE.txt
sudo docker build -t selenium -f Dockerfile_selenium . |& tee SELENIUM_IMAGE.txt

cd ../../
cp ${basedir}/Dockerfile_ddw .
cp ${basedir}/dataworld.py .
sudo docker build -t ddw -f Dockerfile_ddw . |& tee SCRAPER_IMAGE.txt
sudo docker run -it -v $(pwd)/scraper_data:/code/data ddw

popd
