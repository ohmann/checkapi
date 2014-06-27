#!/bin/bash

echo Setting up the CheckAPI SIM for POSIX in directory \'run\'

mkdir run
cp -ansu "$PWD/"*.repy run/
cp -ansu "$PWD/"*.py run/
cp -ansu "$PWD/"*.pyc run/
cp -ansu "$PWD/TRACES/POT/"* run/

echo CheckAPI setup complete
