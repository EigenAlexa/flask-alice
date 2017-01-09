# Local Test Guidelines
*Make sure you do what the caveats tell you or you'll get errors.*
1. Start the app server by running `python app.py` in the root directory.
2. Navigate to the test dir and run `python test.py "<phrase>"`

## Caveats [You must read this to test locally]
**I HIGHLY ENCOURAGE YOU TO USE A VIRTUALENV IN CASE YOU FUCK SHIT UP**
Because Flask_ask requires you to use SSL certificates for verification, using the test script provided in this directory will not work unless you edit the [`verifier.py`](https://github.com/johnwheeler/flask-ask/blob/master/flask_ask/verifier.py) file in your flask_ask installation.

The easiest way to find this is to simply run test.py when your flask server is running. On the console output of your server, you'll see something like
```
File "/Users/philkuz/.virtualenvs/flask-ask/lib/python2.7/site-packages/flask_ask/verifier.py", line 22, in load_certificate
  raise VerificationError("Certificate verification failed")
VerificationError: Certificate verification failed
```
Navigate to that directory, rename `verifier.py` to `verifier.py.bak`, then copy `verifier.py` from this directory into the same directory as `verifier.py.bak`.

When you're done testing and ready to deploy, make sure that you delete `verifier.py` and rename `verifier.py.bak` to `verifier.py`.
