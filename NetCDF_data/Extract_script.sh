#!/bin/bash

d=$PWD

for a in `ls *2085*.7z`; do
   dir=`basename -s .7z $a`
   mkdir $dir
   mv $a $dir
   cd $dir
   7za x $a
   cd $d
   echo $a
done

