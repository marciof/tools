#!/usr/bin/env perl

use defaults;
use Browser::Application::Chrome::Windows ();
use Browser::Application::Firefox::Windows ();

my ($browser) = Browser::Application::Firefox::Windows->new->find;

say $browser->version;
say $browser->path;
$browser->go_to('http://www.example.com');

__END__
sub running {
    my ($class) = @ARG;
    require Win32::Process::Info;
    
    Win32::Process::Info->import;
    my $processes = Win32::Process::Info->new;
    warn "Process list search: " . $processes->Get('variant') . "\n";
    
    foreach my $pid ($processes->ListPids) {
        my ($info) = $processes->GetProcInfo($pid);
        next unless defined($info) && defined($info->{ExecutablePath});
        
        my $executable = Path::Class::File->new($info->{ExecutablePath});
        
        if ($executable->basename eq $EXECUTABLE_NAME) {
            return $class->new(
                path => $executable,
                pid => $info->{ProcessId});
        }
    }
    
    return undef;
}


sub exit {
    my ($self) = @ARG;
    
    if ($self->has_pid) {
        kill POSIX::SIGTERM, $self->pid;
        
        if (kill 0, $self->pid) {
            warn "Process SIGTERM failure: " . $self->pid . "\n";
            eval {kill POSIX::SIGKILL, $self->pid};
            
            if ((my $error = $EVAL_ERROR) ne '') {
                chomp $error;
                warn "Process SIGKILL failure: " . $self->pid . ": $error\n";
                
                require Win32::Process;
                Win32::Process::KillProcess($self->pid, 0);
            }
        }
        
        $self->clear_pid;
    }
    
    return;
}


const my $CANONICAL_OS_NAMES = {
    MSWin32 => 'Windows',
};

has name => (
    is => 'ro',
    isa => 'Str',
    default => sub {
        my ($self) = @ARG;
        my @namespace = split '::', ref $self;
        return pop @namespace;
    },
);


sub load {
    my ($class) = @ARG;
    
    if (defined(my $name = $CANONICAL_OS_NAMES->{$OSNAME})) {
        return Module::Runtime::use_module($class . '::' . $name)->new;
    }
    
    Throwable::Error->throw("Unsupported system: $OSNAME");
}
