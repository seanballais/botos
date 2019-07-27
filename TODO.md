# TODO
Here is a list of things that still needs to be done to improve Botos.

## General
 * Find the rest of the TODO items and move them to here.
 * Maybe add a MBUI file, and add the MBUI texts and the project file path of the file it is residing in to it.

## Views
 * Add the crsf_protect, sensitive_post_parameters, and never_cache decorators,
   if need be, to the POST functions of views.

## Tests
 * Replace app URLs in tests with URL names, i.e. use reverse() instead of
   hard-coded URLs.
 * In test comments, replace hard-coded URLs with their equivalent URL names.
 * Add tests in the test classes in core/tests/index_views.py and
   core/tests/auth_views.py that will test the GET requests of logged-in users.
 * Add a test in VotedSubviewTest in core/tests/index_views.py that will make
   sure that users are shown the voted sub-view immediately after they have
   voted.