package JavaScript::Module;

use defaults;
use Moose;


has dependencies =>,
    is => 'ro',
    isa => 'ArrayRef[JavaScript::Module]',
    default => sub {[]},
    auto_deref => $true;

has file =>,
    is => 'ro',
    isa => 'JavaScript::File',
    required => $true;
