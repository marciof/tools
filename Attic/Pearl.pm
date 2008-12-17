package Pearl;

use base 'Exporter';
use strict;
use utf8;
use warnings;
use Carp;
use English '-no_match_vars';
use IO::Handle;
use Scalar::Util 'openhandle';


our @EXPORT = qw(*STDNULL $false $true const def say);
our $VERSION = 0.1;


sub const(\$$) {
    my ($constant) = shift @ARG;
    return tie $$constant, 'Pearl::Constant::Scalar', shift @ARG;
}


sub def(@) {
    foreach my $value (@ARG) {
        return $Pearl::false unless defined $value;
    }
    return $Pearl::true;
}


sub import {
    English->export_to_level(1);
    Pearl->export_to_level(1);
    
    return 1;
}


# (Modified from Damian Conway's Perl6::Say module, version 0.04.)
sub say(@) {
    my $handle = openhandle $ARG[0] ? shift @ARG : \*STDOUT;
    @ARG = $ARG if @ARG == 0;
    
    my $warning;
    local $SIG{__WARN__} = sub { $warning = join '', @ARG };
    
    push @ARG, "\n" unless $ARG[-1] =~ /\n$/s;
    my $result = print {$handle} @ARG;
    
    croak $warning unless $result;
    return $result;
}


open STDNULL, '+<', $OSNAME eq 'MSWin32' ? 'nul' : '/dev/null';

binmode STDERR, ':utf8';
binmode STDOUT, ':utf8';

autoflush STDERR;
autoflush STDOUT;

const our $false => Pearl::Overloaded::Scalar->new(0, 0, 'false');
const our $true => Pearl::Overloaded::Scalar->new(1, 1, 'true');

$LIST_SEPARATOR = ', ';
$WARNING = $true;

# Needed for object oriented calls:
*IO::Handle::say = \&say unless defined *IO::Handle::say;


################################################################################

# (Modified from Eric J. Roode's Readonly module, version 1.03.)
package Pearl::Constant::Scalar;

use Carp;
use English '-no_match_vars';


sub FETCH {
    my ($self) = @ARG;
    return $$self;
}


sub TIESCALAR {
    # Check for direct ties.
    my $subroutine = (caller 1)[3] || '';
    croak 'Invalid direct tie' unless $subroutine eq 'Pearl::const';
    
    my ($class, $self) = @ARG;
    return bless \$self, $class;
}


*STORE = *UNTIE = sub {
    croak 'Constant values are read-only';
};


################################################################################

package Pearl::Overloaded::Scalar;

use Carp;
use English '-no_match_vars';
use overload
    'bool' => \&to_boolean,
    '0+' => \&to_number,
    '""' => \&to_string;


sub new {
    my ($package) = caller;
    croak 'Internal package' unless $package eq 'Pearl';
    
    my ($class, $boolean, $number, $string) = @ARG;
    my $self = {
        boolean => $boolean,
        number => $number,
        string => $string,
    };
    
    return bless $self, $class;
}


sub to_boolean {
    my ($self) = @ARG;
    return $self->{boolean};
}


sub to_number {
    my ($self) = @ARG;
    return $self->{number};
}


sub to_string {
    my ($self) = @ARG;
    return $self->{string};
}


1

__END__

=head1 NAME

Pearl

=head1 VERSION

0.1 (2008-10-08)

=head1 SYNOPSIS

  use strict;
  use utf8;
  use Pearl;
  #
  const my $PRINT_ERROR => 'Could not print';
  say 'Hello world!' or die $PRINT_ERROR;

=head1 DESCRIPTION

This module automatically imports the English module, defines some defaults and
the following settings:

=over 2

=item

$LIST_SEPARATOR = ', ';

=item

$WARNING = $true;

=back

=head2 CONSTANTS

=over 10

=item C<$false>

Contains boolean, number and string values for false.

=item C<$true>

Contains boolean, number and string values for true.

=back

=head2 FILEHANDLES

=over 10

=item C<STDNULL>

Standard null stream.

=back

=head2 FUNCTIONS

=over 10

=item C<const SCALAR, EXPR>

Creates constant scalars.

=item C<def LIST>

Checks whether all arguments are defined.

=item C<say [FILEHANDLE], LIST>

Alternative to C<print>. Prints a trailing newline only if there isn't one.

=back

=head1 AUTHOR

Márcio Moniz Bandim Faustino

=head1 BUGS

None known.

=head1 SEE ALSO

L<http://search.cpan.org/perldoc?Perl6::Say>,
L<http://search.cpan.org/perldoc?Readonly>

=head1 COPYRIGHT

This module is free software.
You may copy or redistribute it under the same terms as Perl itself.

=cut
