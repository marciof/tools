package Browser::System;

use defaults;
use Moose;
use MooseX::ABC;


with 'MooseX::LogDispatch';
requires qw(execute find);
