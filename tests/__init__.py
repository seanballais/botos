# Do not import any tests here. The Django test runner automatically discovers
# tests inside files whose file names start with 'test'.
#
# Before, test modules didn't have file names that start with 'test'. Each
# test case from the modules were individually imported here. Now, test modules
# have been changed to have file names starting with 'test'. This is so that
# there is no for test cases to be imported here, and to allow us to have
# models that are only available during testing. One test-only model is the
# TestUser model that is used for testing the createsuperuser command.
#
# For more information on Django tests, you may consult this part of the Django
# documentation:
#   https://docs.djangoproject.com/en/2.2/topics/testing/overview/
#
# Note that the documentation is for Django 2.2. When we upgrade to a later
# version of Django, we should update the documentation we are linking to.
