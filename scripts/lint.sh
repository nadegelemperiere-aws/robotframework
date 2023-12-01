#!/bin/bash
# -------------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Scripts to analyze python code quality
# -------------------------------------------------------
# Nadège LEMPERIERE, @19 october 2022
# Latest revision: 19 october 2022
# -------------------------------------------------------

# Retrieve absolute path to this script
script=$(readlink -f $0)
scriptpath=`dirname $script`

docker run -it --rm \
            --volume $scriptpath/..:/package/ \
            nadegelemperiere/terraform-python-awscli:v3.0.0 \
            pylint --rcfile=/package/.pylintrc /package/aws_iac_keywords