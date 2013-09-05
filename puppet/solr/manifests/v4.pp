# TODO: Determine and use latest version by default.
define solr::v4 ($version = '4.4.0', $install_path = '/opt/...') {
    case $operatingsystem {
        'Ubuntu': {
            # External:
            # TODO: Install dependencies automatically.
            include wget # maestrodev/

            package { 'tomcat7':
                ensure => 'installed',
            }

            wget::fetch { 'download':
                source => "http://www.eu.apache.org/dist/lucene/solr/$version/solr-$version.tgz",
                destination => "~/solr-$version.tgz",
            }
        }

        default: {
            fail('Unsupported OS')
        }
    }
}
