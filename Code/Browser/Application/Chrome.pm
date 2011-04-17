package Browser::Application::Chrome;

use defaults;
use Moose;


extends 'Browser::Application';


# --- Instance ---

sub go_to {
    my ($self, $url) = @ARG;
    
    $self->system->execute($self->path, $url);
    return;
}


1;
