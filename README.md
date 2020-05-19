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
