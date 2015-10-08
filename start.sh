#!/bin/sh

export PATH="$PATH:/home/user"

X=$(which X.sh)
autoclick=$(which autoclick.py)
stat2db=$(which stat2db.py)
ssconvert=$(which ssconvert)

download="/home/user/test"
config="autoclick.cfg"
id="2"

$X stop 
$X start

# number of file we expect
nfiles=$($autoclick --conf $config --proxy 127.0.0.1:3128 --id $id --dir $download)

trimspaces() {
	echo $1 | sed -E -e 's/^[ ]//g' -e 's/[ ]$//g'
}

# wait for two files 
while :; do
	count=$(ls $download | wc -l)
 
        count=$(trimspaces $count)
        nfiles=$(trimspaces $nfiles)
        
        if [ -z "$count" ]; then 
        	continue
        elif [ $count -lt $nfiles ]; then
		continue
	else
		break
	fi
done

# do processing 
for file in $(ls $download); do
	base=$(echo "$file" | cut -d'.' -f1)
        $ssconvert "$download/$file" "$download/$base.csv" 2>&1 >/dev/null
        $stat2db --conf $config --file "$download/$base.csv" --id $id
	rm -f "$download/$file" "$download/$base.csv"
done
