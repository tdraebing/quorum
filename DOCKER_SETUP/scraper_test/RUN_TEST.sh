#!/bin/bash

pushd . 
basedir=`pwd`

cd ../
if ! sudo docker --help &>/dev/null; then
	bash install_docker.sh |& tee INSTALL_DOCKER.txt
fi
if [ -d logs ]; then
	mkdir -p logs
fi

cd Dockerfiles
sudo docker build -t ubuntu_miniconda -f Dockerfile_miniconda . |& tee ../logs/MINICONDA_IMAGE.txt
sudo docker build -t selenium -f Dockerfile_selenium . |& tee ../logs/SELENIUM_IMAGE.txt

cd ../../
cp ${basedir}/Dockerfile_ddw .
sudo docker build -t ddw -f Dockerfile_ddw . |& tee DOCKER_SETUP/logs/SCRAPER_IMAGE.txt
sudo docker run -it -v $(pwd)/scraper_data:/code/data ddw |& tee DDW_RUN.txt

popd
