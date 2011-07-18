#!/usr/bin/env perl

# TODO: Take into account multiple packages in a single file.
# TODO: Check and warn for absolute imports only, e.g. "use A ()"
# TODO: Add support for transitive imports, e.g. "use XML::DOM::XPath"
#       implies "use XML::DOM::Parser".
# TODO: Treat "namespace::autoclean" as a pragma?
# TODO: Detect "use English" without any usage of its symbols.


do {
    package PPI::Token::Symbol;
    
    use defaults;
    
    sub uses_module {
        my ($self, $module) = @ARG;
        return $self =~ /^ \Q${\$self->raw_type}$module\E (::\w+) $/x;
    }
};


do {
    package PPI::Token::Word;
    
    use defaults;
    use Module::Runtime ();
    
    sub uses_module {
        my ($self, $module) = @ARG;
        
        return ($self =~ /^ \Q$module\E (::)? $/x)
            || (($self =~ /^ \Q$module\E (::\w+) $/x)
                && !eval {Module::Runtime::require_module($self)});
    }
};


use defaults;
use File::Slurp ();
use PPI ();


my $doc = PPI::Document->new(@ARGV == 0
    ? File::Slurp::slurp(\*STDIN)
    : $ARGV[0]);

my $includes = $doc->find(sub {
    my ($root, $element) = @ARG;
    return $element->isa('PPI::Statement::Include')
        && ($element->type ne 'no')
        && ($element->pragma eq '')
        && ($element->version eq '')
});

exit if $includes eq '';

my $words = $doc->find(sub {
    my ($root, $element) = @ARG;
    return !$element->parent->isa('PPI::Statement::Include')
        && ($element->isa('PPI::Token::Symbol')
            || $element->isa('PPI::Token::Word'));
});

$words = [] if $words eq '';
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
    
    $ARG->uses_module($module) and next INCLUDE foreach @$words;
    
    my ($line, $column) = ($include->line_number, $include->column_number);
    say "Unused $module at line $line"
        . ($column > 1 ? ", column $column." : '.');
}

exit 1;
