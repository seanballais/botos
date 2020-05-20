# botos
An online election system

## Running Tests
Make sure that the development dependencies have been installed before running the tests. To run tests, just simply run:

    $ cd /path/to/project/root/
    $ python manage.py test  # or python3, if you're not using virtual environments.

### Running Tests with Code Coverage
If you would like to have code coverage while running tests, just do the following:

    $ cd /path/to/project/root/
    $ coverage run manage.py test

To view the code coverage report, just do the following:

    $ coverage report

If you want an HTML version of the report, just do the following:

    $ coverage html

The command will produce an HTML version of the report that you can view in the browser with the link, `file://</path/to/project/root>/htmlcov/index.html`, where `</path/to/project/root>` is the absolute path to the root of the project.

## Notes

### Vote Encryption
Botos used to have a vote encryption feature. However, it was removed because it wasn't necessary, as the threat model for this system would make this feature overkill and would even add an additional overhead. It was not also used in a production environment. Botos is only expected to be used in elections where there is a low coercion risk, small-scale elections (the size of a high school or elementary school), where the system is run in a local area network, where voting takes place in a voting station, and where skilled malicious attackers are not prevalent nor non-existent. The threat model assumes that the system administration is the highest security risk for the system. The system administrator has the responsibility of ensuring that no data will be leaked nor modified, and the server configuration is robust enough to repel attacks. If the administrator is corrupt, he/she can rig the elections. Even encrypting votes would not provide adequate security as the system administrator still has access to keys to encrypt and decrypt votes. As such, the vote encryption was removed. It is better to focus on introducing or improving other features instead. The feature may be brought back in the server, but only if there is a reasonable demand for it. If you would like to use a more secure election system, I highly recommend checking [Helios](https://github.com/benadida/helios-server).
