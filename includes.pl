#!/usr/bin/env perl

# TODO: Take into account multiple packages in a single file.
# TODO: Differentiate between A::B::f() and A::f() for a "use A".

use defaults;
use File::Slurp ();
use List::MoreUtils ();
use PPI ();


my $doc = PPI::Document->new(@ARGV == 0
    ? File::Slurp::slurp(\*STDIN)
    : $ARGV[0]);

my $includes = $doc->find(
    sub {
        my ($root, $element) = @ARG;
        return $element->isa('PPI::Statement::Include')
            && ($element->type ne 'no')
            && ($element->pragma eq '')
            && ($element->version eq '')
    
    });

exit unless $includes;

my $words = $doc->find(
    sub {
        my ($root, $element) = @ARG;
        return $element->isa('PPI::Token::Word')
            && !$element->parent->isa('PPI::Statement::Include');
    });

my %uniq_includes;

foreach my $include (@$includes) {
    my $module = $include->module;
    
    if (exists $uniq_includes{$module}) {
        my ($line, $column) = ($include->line_number, $include->column_number);
        say "Duplicate $module at line $line"
            . ($column > 1 ? ", column $column." : '.');
    }
    else {
        $uniq_includes{$module} = $include;
    }
}

foreach my $include (@$includes) {
    my $module = $include->module;
    next if List::MoreUtils::any {$ARG =~ m/^ \Q$module\E \b/x} @$words;
    
    my ($line, $column) = ($include->line_number, $include->column_number);
    say "Unused $module at line $line"
        . ($column > 1 ? ", column $column." : '.');
}
