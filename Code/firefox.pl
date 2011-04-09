#!/usr/bin/env perl

package Browser::Firefox;

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
        my $error = $EXTENDED_OS_ERROR;
        require Win32;
        $error .= ": Administrator rights?" unless Win32::IsAdminUser();
        
        warn "Registry access error: $error\n";
        return $class->_available_from_file_system();
    }
}


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
            return Browser::Firefox->new(
                path => $executable,
                pid => $info->{ProcessId});
        }
    }
    
    return undef;
}


sub _available_from_file_system {
    require Win32;
    my @program_files;
    
    foreach my $variable (qw(%ProgramFiles% %ProgramFiles(x86)%)) {
        my $path = Win32::ExpandEnvironmentStrings($variable);
        push @program_files, $path unless $path eq $variable;
    }
    
    warn "File system search: @program_files\n";
    my @executables;
    
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
    
    return map {Browser::Firefox->new(path => $ARG)} @executables;
}


sub _available_from_registry {
    my ($class, $registry) = @ARG;
    my $key = 'HKEY_LOCAL_MACHINE/SOFTWARE/Wow6432Node/Mozilla/Mozilla Firefox';
    my @executables;
    
    $registry->Delimiter('/');

    foreach my $install ($registry->{$key}->SubKeyNames) {
        my $version = $class->_parse_version($install) or next;
        my $program = $registry->{$key}->{$install}->{'Main/PathToExe'};
        
        push @executables, Browser::Firefox->new(
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
    my $pid = IPC::Open2::open2(undef, undef, $self->path, '-url', $url);
    
    $self->pid($pid) unless $self->has_pid;
    return;
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


sub _get_version {
    my ($self) = @ARG;
    
    # https://developer.mozilla.org/en/Command_Line_Options
    my $pid = IPC::Open2::open2(my $output, undef, $self->path, '--version');
    
    waitpid $pid, 0;
    return $self->_parse_version(join '', <$output>);
}


package main;

use defaults;

my ($firefox) = Browser::Firefox->running || Browser::Firefox->available;

say "--> " . $firefox->version;
$firefox->browse('http://www.example.com');
sleep 5;
$firefox->exit;
