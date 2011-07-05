package JavaScript::File;

use defaults;
use File::Basename ();
use Moose;
use MooseX::Types::Path::Class ();
use Regexp::Common 'comment';


has path =>,
    is => 'ro',
    isa => 'Path::Class::File',
    required => $true,
    coerce => $true;


# --- Class methods ---

sub suffix {
    return '.js';
}


sub suffixes {
    my ($class) = @ARG;
    return $class->test_suffix, $class->suffix;
}


sub test_suffix {
    my ($class) = @ARG;
    return '.test' . $class->suffix;
}


# --- Instance methods ---

sub content {
    my ($self) = @ARG;
    return scalar $self->path->slurp(iomode => '<:encoding(UTF-8)');
}


sub full_name {
    my ($self) = @ARG;
    return scalar File::Basename::fileparse($self->path, $self->suffix);
}


sub is_test {
    my ($self) = @ARG;
    my $suffix = $self->test_suffix;
    
    return $self->path->basename =~ m/\Q$suffix\E$/;
}


sub name {
    my ($self) = @ARG;
    return scalar File::Basename::fileparse($self->path, $self->suffixes);
}


sub requires {
    my ($self) = @ARG;
    my $comment_re = $Regexp::Common::RE{comment}{JavaScript};
    my ($overview) = ($self->content =~ m/^($comment_re)/);
    return () unless defined $overview;
    
    my ($requires) = ($overview =~ m/\@requires \s+ (.+)/x);
    return split m/\s+/, ($requires // '');
}
