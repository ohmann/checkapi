#!/bin/bash

echo Setting up the CheckAPI SIM for RepyV2 in directory \'run\'

mkdir run
cp -ansu "$PWD/Benchmark/"* run/
cp -ansu "$PWD/CheckAPI/"* run/
cp -ansu "$PWD/Repy_Env/"* run/

echo CheckAPI setup complete
