package Browser::Application::Chrome::Windows;

use defaults;
use Moose;

use Browser::Application::Chrome ();


extends 'Browser::System::Windows';

const my $EXECUTABLE_FILE = 'chrome.exe';
const my $EXECUTABLE_LAUNCHER_FILE = 'chrome_launcher.exe';
const my $EXECUTABLE_KEY = 'DisplayIcon';
const my $VENDOR_KEY = join '/',
    qw(HKEY_CURRENT_USER Software Microsoft Windows CurrentVersion Uninstall),
    'Google Chrome';
const my $VERSION_KEY = 'Version';


# --- Instance ---

sub find_in_file_system {
    my ($self) = @ARG;
    my @browsers;
    
    foreach my $path ($self->search_user_files($EXECUTABLE_LAUNCHER_FILE)) {
        my $main_path = $path->dir->parent->file($EXECUTABLE_FILE);
        
        push @browsers, Browser::Application::Chrome->new(
            path => $main_path,
            system => $self,
            version => $self->get_product_version($path));
    }
    
    return @browsers;
}


sub find_in_registry {
    my ($self) = @ARG;
    $self->logger->debug("Registry search: $VENDOR_KEY");
    my $install = $self->registry->{$VENDOR_KEY} // return ();
    
    return Browser::Application::Chrome->new(
        path => $install->{$EXECUTABLE_KEY},
        system => $self,
        version => $install->{$VERSION_KEY});
}
