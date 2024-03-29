Locust Sample project
Plain project to run load testing on API's using locust in python.

Installation
Install python 3 and pip3 in your machine, all the steps are available in this link(https://docs.locust.io/en/stable/installation.html).
The easiest way to install Locust is from PyPI, using pip:
> pip install locust

To run the script: 
> locust -f avocado.py,

then go to http://localhost:8089/ and ten enter the number of users and the ramp up time to get started.

Distributed testing
For distributed testing, locust gives several CLI arguments: –master and –slave, for strict roles determination. 
With this, the machine with master will not simulate loading, but only gather statistics and coordinate the work. 
Let’s try to launch test server and several sessions in distributed mode executing commands in different consoles:
> json-server --watch sample_server/db.json
> locust -f locust_files\locust_file.py --master --host=http://localhost:3000
> locust -f locust_files\locust_file.py --slave --master-host=localhost
> locust -f locust_files\locust_file.py --slave --master-host=localhost, 

Opening the locust in a browser (localhost:8089), you can see that in the right upper corner we have the number of 
machines that will perform the loading.