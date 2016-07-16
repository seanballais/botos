"""Set up the admin upon first install of botos."""
import getpass

from botos.modules.app_data import controllers


def main():
    print('== Botos Admin Setup ==')
    print('Before using Botos, we will setup an admin for your installation.')
    print('This is crucial as the vanilla installation does not create a default admin.')
    print('Press the Enter key to begin setting up an admin.')
    input()

    username = input('Admin username: ')
    password = getpass.getpass('Admin password: ')

    controllers.User.add(username,
                         password,
                         '',
                         'admin'
                         )

    print('Admin {0} has now been created.'.format(username))
    print('You may now log in to the app using the recently created admin credentials.')

if __name__ == '__main__':
    main()