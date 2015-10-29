#!/bin/sh

export PATH="$PATH:/home/user"

X=$(which X.sh)
autoclick=$(which autoclick.py)
stat2db=$(which stat2db.py)
ssconvert=$(which ssconvert)

download="/home/user/test"
config="autoclick.cfg"
id="139"

$X stop 
$X start

# number of file we expect
nfiles=$($autoclick --conf $config --proxy 127.0.0.1:3128 --id $id --dir $download)

trimspaces() {
	echo "$1" | sed -E -e 's/^[[:space:]]+//g' -e 's/[[:space:]]+$//g'
}

strstr() {
	echo $1 | awk -v pattern=$2 ' $0 ~ pattern { print 1; } $0 !~ pattern { print 0; }'
}

# wait for two files 
while :; do
	count=$(ls $download | wc -l)
 
        count=$(trimspaces $count)
        nfiles=$(trimspaces $nfiles)
        
        if [ -z "$count" ] || [ $count -lt $nfiles ]; then
		continue
	else
		break
	fi
done

# do processing 
for file in $(ls $download); do
	base=$(echo "$file" | cut -d'.' -f1)
        $ssconvert "$download/$file" "$download/$base.csv" 2>&1 1>/dev/null
        match=$(strstr "$file" "campaign")
        if [ $match -eq 1 ]; then
          stat2db-login.py --conf $config --file "$download/$base.csv" --id $id
        else
	  $stat2db --conf $config --file "$download/$base.csv" --id $id
	fi
        rm -f "$download/$file" "$download/$base.csv"
done
