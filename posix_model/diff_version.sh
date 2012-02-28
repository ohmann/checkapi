
files=`ls | egrep -v "README|tests|diff_version.sh"`

for F in $files
do
    diff -q $1$F $F
done