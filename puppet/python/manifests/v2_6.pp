class python::v2_6 {
    case $operatingsystem {
        # http://askubuntu.com/a/141664/163034
        'Ubuntu': {
            # External:
            # TODO: Install dependencies automatically.
            include apt # puppetlabs/

            # TODO: Check first if there's a package available.
            apt::ppa { 'ppa:fkrull/deadsnakes':
            }

            package { 'python2.6':
                ensure => 'installed',
            }
        }

        default: {
            fail('Unsupported OS')
        }
    }
}
