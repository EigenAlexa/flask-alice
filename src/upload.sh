zip -r code.zip src
aws lambda update-function-code --function-name JamesTestEigen --zip-file fileb://code.zip 
