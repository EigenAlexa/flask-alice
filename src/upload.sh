FORMAT="Command should be formatted as 'upload.sh <dir> <function-name>'"
ZIPFILE="code.zip"
if [ $# -ne 2 ]; then
    echo $FORMAT 
    exit 1
elif [ $# -eq 2 ]; then
    dir=$1
    funcname=$2
fi
zip -r $ZIPFILE $dir
aws --region us-east-1 lambda update-function-code --function-name $funcname --zip-file fileb://$ZIPFILE
