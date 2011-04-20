package Browser::Application::Opera::Windows;

use defaults;
use List::MoreUtils ();
use Moose;
use Path::Class::File ();

use Browser::Application::Opera ();


extends 'Browser::System::Windows';

const my $EXECUTABLE_FILE = 'opera.exe';
const my $PATH_KEY = 'InstallLocation';
const my $UNINSTALL_KEY = "HKEY_LOCAL_MACHINE/SOFTWARE/$Browser::System::Windows::WIN64_KEY/Microsoft/Windows/CurrentVersion/Uninstall";
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
    my @browsers;
    my @paths = List::MoreUtils::uniq(
        $self->_find_in_registry_install,
        $self->_find_in_registry_uninstall);
    
    foreach my $path (@paths) {
        push @browsers, Browser::Application::Opera->new(
            path => $path,
            system => $self,
            version => $self->get_product_version($path));
    }
    
    return @browsers;
}


sub _find_in_registry_install {
    my ($self) = @ARG;
    my $information = $self->registry->{$VENDOR_KEY};
    my @paths;
    
    $self->logger->debug("Registry search: $VENDOR_KEY");
    
    while (my ($key, $value) = each %$information) {
        if ($key =~ m/\b (directory | path) \b/ix) {
            my $path = Path::Class::File->new($value, $EXECUTABLE_FILE);
            push @paths, $path if -e $path;
        }
        elsif ($key =~ m/\b CommandLine \b/ix) {
            my ($path) = ($value =~ m/^(.+ \Q$EXECUTABLE_FILE\E)/x);
            push @paths, $path if -e $path;
        }
    }
    
    return @paths;
}


sub _find_in_registry_uninstall {
    my ($self) = @ARG;
    my $uninstall = $self->registry->{$UNINSTALL_KEY};
    my @paths;
    
    $self->logger->debug("Registry search: $UNINSTALL_KEY");
    return () unless defined $uninstall;
    
    foreach my $application (grep m/^Opera\b/, $uninstall->SubKeyNames) {
        my $path = $uninstall->{$application}{$PATH_KEY};
        push @paths, Path::Class::File->new($path, $EXECUTABLE_FILE);
    }
    
    return @paths;
}
