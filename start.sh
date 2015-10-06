#!/bin/sh

export PATH="$PATH:/home/user"

X=$(which X.sh)
autoclick=$(which autoclick.py)
stat2db=$(which stat2db.py)
ssconvert=$(which ssconvert)

download="/home/user/test"
config="autoclick.cfg"

$X stop 
$X start

$autoclick --conf $config --proxy 127.0.0.1:3128 --id 1 --dir $download

# wait for two files 
while :; do
	count=$(ls $download | wc -l)
	if [ $count -lt 2 ]; then
		sleep 2
	else
		break
	fi
done

for file in $(ls $download); do
	base=$(echo "$file" | cut -d'.' -f1)
        $ssconvert "$download/$file" "$download/$base.csv" 2>&1 >/dev/null
        $stat2db --file "$download/$base.csv"
	rm -f "$download/$file"
done
