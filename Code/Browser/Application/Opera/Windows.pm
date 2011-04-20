package Browser::Application::Opera::Windows;

use defaults;
use Moose;
use Path::Class::File ();

use Browser::Application::Opera ();


extends 'Browser::System::Windows';

const my $EXECUTABLE_FILE = 'opera.exe';
const my $VENDOR_KEY = 'HKEY_CURRENT_USER/Software/Opera Software';


# --- Instance ---

sub find_in_file_system {
    my ($self) = @ARG;
    my @browsers;
    
    foreach my $path ($self->search_program_files($EXECUTABLE_FILE)) {
        push @browsers, Browser::Application::Opera->new(
            path => $path,
            system => $self,
            version => $self->get_product_version($path));
    }
    
    return @browsers;
}


sub find_in_registry {
    my ($self) = @ARG;
    my $information = $self->registry->{$VENDOR_KEY};
    my @browsers;
    
    $self->logger->debug("Registry search: $VENDOR_KEY");
    
    while (my ($key, $value) = each %$information) {
        next unless $key =~ m/\b (directory | path) \b/ix;
        
        my $path = Path::Class::File->new($value, $EXECUTABLE_FILE);
        next unless -e $path;
        
        push @browsers, Browser::Application::Opera->new(
            path => $path,
            system => $self,
            version => $self->get_product_version($path));
    }
    
    return @browsers;
}
