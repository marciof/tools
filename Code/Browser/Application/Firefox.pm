package Browser::Application::Firefox;

use defaults;
use Moose;


extends 'Browser::Application';

has '+version' =>
    required => $false,
    writer => '_set_version';


# --- Class ---

sub parse_version {
    my ($class, $version) = @ARG;
    
    $version =~ m/(\d+ (?: \.\d+) +)/x;
    return $1;
}


# --- Instance ---

sub BUILD {
    my ($self) = @ARG;
    
    unless (defined $self->version) {
        $self->logger->debug('Version inquiry: ' . $self->path);
        $self->_set_version($self->_get_version);
    }
    
    return;
}


sub go_to {
    my ($self, $url) = @ARG;
    
    $self->system->execute($self->path, '-url', $url);
    return;
}


sub _get_version {
    my ($self) = @ARG;
    
    return try {
        $self->system->get_product_version($self->path);
    }
    catch {
        $self->logger->debug($ARG->message);
        my $output = $self->system->execute($self->path, '--version');
        $self->parse_version($output);
    };
}
