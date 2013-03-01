#!/bin/bash
#
# This is a generic python runner script that sets up proper PYTHONPATH based
# on the project's Makefile's PYTHONPATH target. This script allows users
# to execute any script on multiple projects without having to manually
# hard set PYTHONPATH in the environment.
#
# Usage: symbolic link this script as <program>.sh to the location of
# <program>.py

set -e
makefile_dir=`dirname $0`
count=1
while [ ! -e "$makefile_dir/Makefile" -a $count -lt 10 ]; do
  makefile_dir="$makefile_dir/.."
  count=`expr $count + 1`
done

if [ ! -e "$makefile_dir/Makefile" ]; then
  echo "Cannot find Makefile."
  exit 1
fi

pythonpath=`make -C $makefile_dir PYTHONPATH | grep PYTHONPATH`
project_env=`make -C $makefile_dir print | grep PROJECT_ENV`
if [[ "$pythonpath" =~ 'PYTHONPATH' ]]; then
  filename=`basename $0`
  filename=`echo $filename | sed -e 's/\.sh//'`
  full_filename="`dirname $0`/$filename.py"
  if [ ! -e $full_filename ]; then
    echo "Cannot find $full_filename"
    exit 1
  fi
  export $project_env
  export $pythonpath
  cmd="python `dirname $0`/$filename.py $*"
  echo "% $project_env $pythonpath $cmd"
  $cmd 2>&1
else
  echo "Makefile does not have a $PYTHONPATH target ($pythonpath)."
  exit 1
fi

