package Browser::System::Windows;

use defaults;
use File::Basename ();
use File::Find ();
use IPC::Open2 ();
use Moose;
use MooseX::ABC;
use Path::Class::Dir ();
use Path::Class::File ();
use Perl6::Slurp ();
use Throwable::Error ();
use Win32 ();
use Win32::File::VersionInfo ();
use Win32::TieRegistry ();


extends 'Browser::System';
requires qw(find_in_file_system find_in_registry);

const our $WIN64_KEY = 'Wow6432Node';
const my $PROGRAM_FILES = [qw{%ProgramFiles(x86)% %ProgramFiles%}];
const my $SKIP_PROGRAMS = qr/^ (?: Common | Microsoft | Windows)/ix;
const my $USER_FILES = [
    Path::Class::Dir->new('%USERPROFILE%', 'Local Settings', 'Application Data'),
    '%LOCALAPPDATA%',
];

has registry =>
    is => 'ro',
    isa => 'Win32::TieRegistry',
    lazy => $true,
    default => \&_load_registry;


# --- Instance ---

sub execute {
    my $self = shift @ARG;
    
    my $pid = IPC::Open2::open2(my $output, undef, @ARG);
    return unless defined wantarray;
    waitpid $pid, 0;
    
    my $output_string = Perl6::Slurp::slurp($output);
    close $output;
    return $output_string;
}


sub find {
    my ($self) = @ARG;
    
    return try {
        $self->find_in_registry;
    }
    catch {
        $self->logger->debug($ARG->message);
        $self->find_in_file_system;
    };
}


sub get_product_version {
    my ($self, $executable) = @ARG;
    my $info = Win32::File::VersionInfo::GetFileVersionInfo($executable);
    
    unless (defined $info) {
        Throwable::Error->throw("$EXTENDED_OS_ERROR: " . $executable);
    }
    
    my $lang = each %{$info->{Lang}};
    return $info->{Lang}{$lang}{ProductVersion} // $info->{ProductVersion};
}


sub search_program_files {
    my ($self, $executable) = @ARG;
    return $self->_search_programs($executable, @$PROGRAM_FILES);
}


sub search_user_files {
    my ($self, $executable) = @ARG;
    return $self->_search_programs($executable, @$USER_FILES);
}


sub _search_programs {
    my ($self, $executable, @paths) = @ARG;
    my @resolved_paths = map {Win32::ExpandEnvironmentStrings($ARG)} @paths;
    my $file_name = File::Basename::fileparse($executable, '.exe');
    my @executables;
    
    do {
        no warnings 'File::Find';
        $self->logger->debug("File system search: @resolved_paths");
        
        File::Find::find({
            preprocess => sub {
                my @likely = grep m/\Q$file_name\E/i, @ARG;
                return @likely > 0
                    ? @likely
                    : grep {$ARG !~ $SKIP_PROGRAMS} @ARG;
            },
            wanted => sub {
                if ($ARG eq $executable) {
                    push @executables, Path::Class::File->new($File::Find::name);
                }
            },
        }, @resolved_paths);
    };
    
    return @executables;
}


sub _load_registry {
    my $registry = $Win32::TieRegistry::Registry;
    
    if (defined $registry->{HKEY_LOCAL_MACHINE}) {
        $registry->Delimiter('/');
        return $registry;
    }
    else {
        my @error = ('Registry access error', $EXTENDED_OS_ERROR);
        
        push @error, 'Not an administrator' unless Win32::IsAdminUser;
        Throwable::Error->throw(join ': ', @error);
    }
}
