#!/bin/bash

# always response as one liner with all the variables
composeFilePath="./src/main/docker/docker-compose.yml"
envFile="./src/main/docker/.env"

INSTALL_OPTION=$1
if [[ "$INSTALL_OPTION" == "-r" ]]; then
    docker-compose -f "${composeFilePath}" --project-directory ./ --env-file "${envFile}"  up -d
elif [[ "$INSTALL_OPTION" == "-b" ]]; then
    docker-compose -f "${composeFilePath}" --project-directory ./ --env-file "${envFile}" build
elif [[ "$INSTALL_OPTION" == "-s" ]]; then
    docker-compose -f "${composeFilePath}" --project-directory ./ --env-file "${envFile}" stop
elif [[ "$INSTALL_OPTION" == "-d" ]]; then
    docker-compose -f "${composeFilePath}" --project-directory ./ --env-file "${envFile}" stop && docker-compose -f ./src/main/docker/docker-compose.yml --project-directory ./ --env-file "${envFile}" down
elif [[ "$INSTALL_OPTION" == "-l" ]]; then
    docker-compose -f "${composeFilePath}" --project-directory ./ --env-file "${envFile}"  logs -f
else
    echo "Missing or wrong arguments:"
    echo "Try -b for building"
    echo "Try -d for downing everything"
    echo "Try -s for stopping"
    echo "Try -l for logging"
    echo "Try -r for running the project"
    echo "Example: bash app.sh -d"
fi