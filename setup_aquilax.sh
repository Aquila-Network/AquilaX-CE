#!/bin/bash -e

# create aquilax data directory
mkdir -p ${HOME}/aquilax/
mkdir -p ${HOME}/aquilax/src
mkdir -p ${HOME}/aquilax/data
mkdir -p ${HOME}/aquilax/data/models
mkdir -p ${HOME}/aquilax/ossl

echo "================================"
echo "==== Downloading Base Model ===="
echo "================================"
wget -c "https://ftxt-models.s3.us-east-2.amazonaws.com/wiki_100d_en.bin" -P ${HOME}/aquilax/data/models/

# setup ossl keys
if ! test -f ${HOME}/aquilax/ossl/private.pem; then
    openssl genrsa -passout pass:1234 -des3 -out ${HOME}/aquilax/ossl/private.pem 2048
fi
if ! test -f ${HOME}/aquilax/ossl/public.pem; then
    openssl rsa -passin pass:1234 -in ${HOME}/aquilax/ossl/private.pem -outform PEM -pubout -out ${HOME}/aquilax/ossl/public.pem
fi
if ! test -f ${HOME}/aquilax/ossl/private_unencrypted.pem; then
    openssl rsa -passin pass:1234 -in ${HOME}/aquilax/ossl/private.pem -out ${HOME}/aquilax/ossl/private_unencrypted.pem -outform PEM
fi

# build aqiladb image
docker build https://raw.githubusercontent.com/Aquila-Network/AquilaDB/master/Dockerfile -t aquiladb:local

# build aqilahub image
docker build https://raw.githubusercontent.com/Aquila-Network/AquilaHub/main/Dockerfile -t aquilahub:local

# build aquilax image
docker build Dockerfile -t aquilax:local

echo ${HOME}/aquilax/ossl

# run docker compose
cd ${HOME}/aquilax/src
git clone https://github.com/Aquila-Network/AquilaX-CE.git .
docker-compose up
