#!/usr/bin/env perl


# TODO: Add tests.
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
        return $self =~ /^ \Q${\$self->raw_type}$module\E :: (\w+)? $/x;
    }
};


do {
    package PPI::Token::Word;
    
    use defaults;
    use Module::Runtime ();
    
    
    sub uses_module {
        my ($self, $module) = @ARG;
        
        return ($self =~ /^ \Q$module\E (::)? $/x)
            || (($self =~ /^ \Q$module\E :: \w+ $/x)
                && !eval {Module::Runtime::require_module($self)});
    }
};


do {
    package Includes;
    
    use defaults;
    use PPI::Document ();
    use Set::Scalar ();
    
    
    sub analyze {
        my ($class, $input, $handler) = @ARG;
        my $document = PPI::Document->new($input);
        my $included_modules = Set::Scalar->new;
        my @tokens = $class->list_tokens($document);
        my @defects;
        
        $handler //= sub {
            my ($defect, $include) = @ARG;
            push @defects, {$defect => $include};
        };
        
        INCLUDE:
        foreach my $include ($class->list_includes($document)) {
            my $module = $include->module;
            
            if ($included_modules->has($module)) {
                $handler->(duplicate => $include);
            }
            else {
                $included_modules->insert($module);
            }
            
            $ARG->uses_module($module) and next INCLUDE foreach @tokens;
            $handler->(unused => $include);
        }
        
        return ($document, @defects);
    }
    
    
    sub list_includes {
        my ($class, $document) = @ARG;
        
        my $includes = $document->find(sub {
            my ($root, $element) = @ARG;
            
            return $element->isa('PPI::Statement::Include')
                && ($element->type ne 'no')
                && ($element->pragma eq '')
                && ($element->version eq '')
        });
        
        return ($includes eq '') ? () : @$includes;
    }
    
    
    sub list_tokens {
        my ($class, $document) = @ARG;
        
        my $tokens = $document->find(sub {
            my ($root, $element) = @ARG;
            
            return $element->isa('PPI::Statement::Include')
                ? undef
                : $element->isa('PPI::Token::Symbol')
                    || $element->isa('PPI::Token::Word');
        });
        
        return ($tokens eq '') ? () : @$tokens;
    }
};


do {
    package Includes::Test;
    
    use defaults;
    use base 'Test::Class';
    use Test::More;
    
    
    sub duplicate : Test(5) {
        my ($doc, @defects) = Includes->analyze(\<< '');
use Carp;
use Carp ();
use Carp 'confess';

        foreach my $i (0 .. $#defects) {
            ok(exists $defects[$i]{(($i % 2) == 0) ? 'unused' : 'duplicate'});
        }
    }
    
    
    sub unused : Test(3) {
        my @variations = (
            'use Carp',
            'use Carp ()',
            q{use Carp 'confess'},
        );
        
        foreach my $code (@variations) {
            my ($doc, $defect) = Includes->analyze(\$code);
            ok(exists $defect->{unused});
        }
    }
    
    
    sub unused_with_label : Test(1) {
        my ($doc, $defect) = Includes->analyze(\<< '');
use Carp ();
Carp:;

        ok(exists $defect->{unused});
    }
    
    
    sub use_module_namespace : Test(1) {
        my ($doc, @defects) = Includes->analyze(\<< '');
use Carp ();
%Carp::;

        is(scalar(@defects), 0);
    }
    
    
    sub use_module_literal : Test(1) {
        my ($doc, @defects) = Includes->analyze(\<< '');
use Carp ();
Carp::;

        is(scalar(@defects), 0);
    }
    
    
    sub use_module_scalar : Test(1) {
        my ($doc, @defects) = Includes->analyze(\<< '');
use Carp ();
$Carp::Verbose = 1;

        is(scalar(@defects), 0);
    }
};


use defaults;

unless (caller) {
    die "Usage: file\n" if @ARGV == 0;
    
    Includes->analyze($ARGV[0], sub {
        my ($defect, $include) = @ARG;
        
        printf "%s %s at line %d.\n",
            ucfirst($defect), $include->module, $include->line_number;
    });
}
