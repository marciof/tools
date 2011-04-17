package Browser::Application;

use defaults;
use Moose;
use MooseX::ABC;
use MooseX::Types::Path::Class ();


with 'MooseX::LogDispatch';
requires 'go_to';

has path =>
    is => 'ro',
    isa => 'Path::Class::File',
    required => $true,
    coerce => $true;

has system =>
    is => 'ro',
    isa => 'Browser::System',
    required => $true;

has version =>
    is => 'ro',
    isa => 'Str',
    required => $true;
