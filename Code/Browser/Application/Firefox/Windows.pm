package Browser::Application::Firefox::Windows;

use defaults;
use Moose;

use Browser::Application::Firefox ();


extends 'Browser::System::Windows';

const my $EXECUTABLE_FILE = 'firefox.exe';
const my $EXECUTABLE_KEY = 'Main/PathToExe';
const my $SOFTWARE_KEY = 'HKEY_LOCAL_MACHINE/SOFTWARE';
const my $VENDOR_KEY = 'Mozilla/Mozilla Firefox';
const my $WIN64_KEY = 'Wow6432Node';


# --- Instance ---

sub find_in_file_system {
    my ($self) = @ARG;
    my @browsers;
    
    foreach my $path ($self->search_program_files($EXECUTABLE_FILE)) {
        my %version = try {
            version => $self->get_product_version($path);
        }
        catch {
            $self->logger->debug($ARG->message);
            ();
        };
        
        push @browsers, Browser::Application::Firefox->new(
            path => $path,
            system => $self,
            %version);
    }
    
    return @browsers;
}


sub find_in_registry {
    my ($self) = @ARG;
    my @browsers;
    
    my @keys = grep {defined $ARG} map {$self->registry->{$ARG}}
        "$SOFTWARE_KEY/$WIN64_KEY/$VENDOR_KEY",
        "$SOFTWARE_KEY/$VENDOR_KEY";
    
    foreach my $key (@keys) {
        $self->logger->debug('Registry search: ' . $key->Path);
        
        foreach my $install ($key->SubKeyNames) {
            my $version = Browser::Application::Firefox->parse_version($install);
            next unless defined $version;
            my $path = $key->{$install}->{$EXECUTABLE_KEY};
            
            push @browsers, Browser::Application::Firefox->new(
                path => $path,
                system => $self,
                version => $version);
        }
    }
    
    return @browsers;
}
