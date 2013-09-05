class java::v7 {
    case $operatingsystem {
        # https://help.ubuntu.com/community/Java
        'Ubuntu': {
            # External:
            # TODO: Install dependencies automatically.
            include apt # puppetlabs/

            # TODO: Check first if there's a package available.
            apt::ppa { 'ppa:webupd8team/java':
            }

            package { 'oracle-java7-installer':
                ensure => 'installed',
            }
        }

        default: {
            fail('Unsupported OS')
        }
    }
}
