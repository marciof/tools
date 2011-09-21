#!/usr/bin/env perl

# TODO: Take into account multiple packages in a single file.
# TODO: Check and warn for absolute imports only, e.g. "use A ();"

use defaults;
use File::Slurp ();
use Module::Runtime ();
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

exit unless defined $includes;

my $words = $doc->find(
    sub {
        my ($root, $element) = @ARG;
        return !$element->parent->isa('PPI::Statement::Include')
            && ($element->isa('PPI::Token::Word')
                || $element->isa('PPI::Token::Symbol'));
    });

my %uniq_includes;

INCLUDE:
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
    
    foreach my $word (@$words) {
        if ($word->isa('PPI::Token::Word')) {
            next INCLUDE if
                $word eq $module
                || (($word =~ /^ \Q$module\E (::\w+) $/x)
                    && !eval {Module::Runtime::require_module($word)});
        }
        elsif ($word->isa('PPI::Token::Symbol')) {
            next INCLUDE if
                $word =~ /^ \Q${\$word->raw_type}$module\E (::\w+) $/x;
        }
        else {
            die "Unknown word: " . ref($word) . ": $word";
        }
    }
    
    my ($line, $column) = ($include->line_number, $include->column_number);
    say "Unused $module at line $line"
        . ($column > 1 ? ", column $column." : '.');
}
