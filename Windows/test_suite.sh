#!/bin/bash

failures=`cat << !EOF
[ ! "Missing the shape to create" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png >/dev/null
[ ! "Incorrect config file" ]
./emboss.py --config ./BfB3000_config.err --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cylinder >/dev/null
[ ! "Incorrect image file" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.err cylinder >/dev/null
[ ! "Incorrect prefix file" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.err --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cylinder >/dev/null
[ ! "Incorrect suffix file" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.err --image ./bfblogo.png cylinder >/dev/null
[ ! "Incorrect output file" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --output /tmp/ cylinder >/dev/null
[ ! "Negative height" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --height -100.0 cylinder >/dev/null
[ ! "Zero height" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --height 0.0 cylinder >/dev/null
[ ! "Ridiculous height" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --height 1000.0 cylinder >/dev/null
[ ! "Negative bottom layers" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --bottomLayers -100 cylinder >/dev/null
[ ! "Zero bottom layers" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --bottomLayers 0 cylinder >/dev/null
[ ! "Ridiculous bottom layers" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --bottomLayers 100 cylinder >/dev/null
[ ! "Negative embossing" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --embossFactor -1.0 cylinder >/dev/null
[ ! "Zero embossing" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --embossFactor 0.0 cylinder >/dev/null
[ ! "Insufficient embossing" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --embossFactor 0.24 cylinder >/dev/null
[ ! "Excessive embossing" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --embossFactor 1.01 cylinder >/dev/null
[ ! "Negative radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cylinder --radius -10.0 >/dev/null
[ ! "Zero radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cylinder --radius 0.0 >/dev/null
[ ! "Insufficient radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cylinder --radius 4.99 >/dev/null
[ ! "Excessive radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cylinder --radius 200.0 >/dev/null
[ ! "Negative cone bottom radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cone --rbot -10.0 >/dev/null
[ ! "Zero cone bottom radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cone --rbot 0.0 >/dev/null
[ ! "Insufficent cone bottom radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cone --rbot 4.99 >/dev/null
[ ! "Excessive cone bottom radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cone --rbot 200.0 >/dev/null
[ ! "Negative cone top radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cone --rtop -10.0 >/dev/null
[ ! "Zero cone top radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cone --rtop 0.0 >/dev/null
[ ! "Insufficent cone top radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cone --rtop 4.99 >/dev/null
[ ! "Excessive cone top radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cone --rtop 200.0 >/dev/null
[ ! "Cone top radius = bottom radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cone --rbot 25 --rtop 25 >/dev/null
[ ! "Cone top radius > bottom radius" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png cone --rbot 25 --rtop 25.1 >/dev/null
[ ! "Cone top radius << bottom radius - excessive overhangs" ]
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --height 10 cone --rbot 50.00 --rtop 5.00 >/dev/null

!EOF`

successes=`cat << !EOF
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --output ./c_cylinder.bfb  --zsmooth        cylinder --radius 20.0
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --output ./c_cone.bfb      --zsmooth        cone     --rbot 30.0 --rtop 20.0
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./globe.png --output ./c_globe.bfb     --zsmooth        globe
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --output ./b2_cylinder.bfb --bottomLayers 2 cylinder
./emboss.py --config ./BfB3000_config.txt --prefix ./BfB3000_prefix.txt --suffix ./BfB3000_suffix.txt --image ./bfblogo.png --output /dev/null         -v               cylinder
!EOF`

echo -e "\nExpected Failure scenarios"
echo "${failures}" | while read line
do
  /bin/bash -c "${line}"
  status=$?
  echo -ne "${status}\t: ${line}\n"
  if [ ${status} == 0 ]
  then
    echo -e "***\n*** Warning - unexpected success\n***"
  fi
done

echo -e "\nExpected success scenarios"
echo "${successes}" | while read line
do
  /bin/bash -c "${line}"
  status=$?
  echo -ne "${status}\t: ${line}\n"
  if [ ${status} != 0 ]
  then
    echo -e "***\n*** Warning - unexpected failure\n***"
  fi
done

