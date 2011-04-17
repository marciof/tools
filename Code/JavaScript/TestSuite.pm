package JavaScript::TestSuite;

use defaults;
use Moose;


has implementations =>,
    is => 'ro',
    isa => 'ArrayRef[JavaScript::Module]',
    required => $true,
    auto_deref => $true;

has tests =>,
    is => 'ro',
    isa => 'ArrayRef[JavaScript::Module]',
    required => $true,
    auto_deref => $true;


# --- Instance ---

sub modules {
    my ($self) = @ARG;
    return $self->implementations, $self->tests;
}
