#!/usr/bin/env perl

package Firefox;

# TODO: Terminate processes cleanly, http://support.microsoft.com/kb/178893.
# TODO: Abstract OS specific code.

use defaults;
use File::Find ();
use IPC::Open2 ();
use Moose;
use MooseX::Types::Path::Class;
use POSIX ();


has path => (
    is => 'ro',
    isa => 'Path::Class::File',
    required => $true,
    coerce => $true,
);

has pid => (
    is => 'rw',
    isa => 'Str',
    clearer => 'clear_pid',
    predicate => 'has_pid',
);

has version => (
    is => 'ro',
    isa => 'Str',
    lazy => $true,
    default => \&_get_version,
);

const my $EXECUTABLE_NAME = 'firefox.exe';


# --- Class methods ---

sub available {
    my ($class) = @ARG;
    require Win32::TieRegistry;
    
    if (defined $Win32::TieRegistry::Registry->{'HKEY_LOCAL_MACHINE'}) {
        return $class->_available_from_registry($Win32::TieRegistry::Registry);
    }
    else {
        return $class->_available_from_file_system();
    }
}


sub running {
    my ($class) = @ARG;
    require Win32::Process::Info;
    
    Win32::Process::Info->import;
    my $processes = Win32::Process::Info->new;

    foreach my $pid ($processes->ListPids) {
        my ($info) = $processes->GetProcInfo($pid);
        next unless defined($info) && defined($info->{ExecutablePath});
        
        my $executable = Path::Class::File->new($info->{ExecutablePath});
        
        if ($executable->basename eq $EXECUTABLE_NAME) {
            return Firefox->new(
                path => $executable,
                pid => $info->{ProcessId});
        }
    }
    
    return undef;
}


sub _available_from_file_system {
    require Win32;
    
    my @program_files;
    my @executables;
    
    foreach my $variable (qw(%ProgramFiles% %ProgramFiles(x86)%)) {
        my $path = Win32::ExpandEnvironmentStrings($variable);
        push @program_files, $path unless $path eq $variable;
    }
    
    File::Find::find({
        preprocess => sub {
            my @likely = grep m/Firefox/i, @ARG;
            return @likely > 0
                ? @likely
                : grep !m/^ (?: Common | Microsoft | Windows)/ix, @ARG;
        },
        wanted => sub {
            push @executables, $File::Find::name if $ARG eq $EXECUTABLE_NAME;
        },
    }, @program_files);
    
    return map {Firefox->new(path => $ARG)} @executables;
}


sub _available_from_registry {
    my ($class, $registry) = @ARG;
    my $key = 'HKEY_LOCAL_MACHINE/SOFTWARE/Wow6432Node/Mozilla/Mozilla Firefox';
    my @executables;
    
    $registry->Delimiter('/');

    foreach my $install ($registry->{$key}->SubKeyNames) {
        my $version = $class->_parse_version($install) or next;
        my $program = $registry->{$key}->{$install}->{'Main/PathToExe'};
        
        push @executables, Firefox->new(
            path => $program,
            version => $version);
    }
    
    return @executables;
}


sub _parse_version {
    my ($class, $version) = @ARG;
    
    $version =~ m/(\d+ (?: \.\d+) +)/x;
    return $1;
}


# --- Instance methods ---

sub browse {
    my ($self, $url) = @ARG;
    my @program = ($self->path, '-url', $url);
    my $pid = IPC::Open2::open2(undef, undef, @program);
    
    $self->pid($pid) unless $self->has_pid;
    return;
}


sub exit {
    my ($self) = @ARG;
    
    if ($self->has_pid) {
        kill POSIX::SIGTERM, $self->pid;
        
        if (kill 0, $self->pid) {
            eval {kill POSIX::SIGKILL, $self->pid};
            
            if ($EVAL_ERROR ne '') {
                require Win32::Process;
                Win32::Process::KillProcess($self->pid, 0);
            }
        }
        
        $self->clear_pid;
    }
    
    return;
}


sub _get_version {
    my ($self) = @ARG;
    my $pid = IPC::Open2::open2(my $output, undef, $self->path, '--version');
    
    waitpid $pid, 0;
    return $self->_parse_version(join '', <$output>);
}


package main;

use defaults;

my ($firefox) = Firefox->running || Firefox->available;

say $firefox->version;
$firefox->browse('http://www.example.com');
sleep 5;
$firefox->exit;
