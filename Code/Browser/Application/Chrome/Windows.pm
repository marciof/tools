package Browser::Application::Chrome::Windows;

use defaults;
use Moose;

use Browser::Application::Chrome ();


extends 'Browser::System::Windows';

const my $EXECUTABLE_FILE = 'chrome.exe';
const my $EXECUTABLE_LAUNCHER_FILE = 'chrome_launcher.exe';
const my $EXECUTABLE_KEY = 'DisplayIcon';
const my $VENDOR_KEY = 'HKEY_CURRENT_USER/Software/Microsoft/Windows/CurrentVersion/Uninstall/Google Chrome';
const my $VERSION_KEY = 'Version';


# --- Instance ---

sub find_in_file_system {
    my ($self) = @ARG;
    my @browsers;
    
    foreach my $path ($self->search_user_files($EXECUTABLE_LAUNCHER_FILE)) {
        my $main_path = $path->dir->parent->file($EXECUTABLE_FILE);
        
        my $version = try {
            $self->get_product_version($path);
        }
        catch {
            $self->logger->debug($ARG->message);
            $path->dir->dir_list(-1);
        };
        
        push @browsers, Browser::Application::Chrome->new(
            path => $main_path,
            system => $self,
            version => $version);
    }
    
    return @browsers;
}


sub find_in_registry {
    my ($self) = @ARG;
    my $install = $self->registry->{$VENDOR_KEY};
    $self->logger->debug('Registry search: ' . $VENDOR_KEY);
    
    return Browser::Application::Chrome->new(
        path => $install->{$EXECUTABLE_KEY},
        system => $self,
        version => $install->{$VERSION_KEY});
}
