#!/usr/bin/env perl


# TODO: Add tests.
# TODO: String interpolation.
# TODO: Multiple packages in a single file.
# TODO: Warn for absolute imports only, e.g. "use A ()"
# TODO: Transitive imports, e.g. XML::DOM::XPath implies XML::DOM::Parser.
# TODO: Treat "namespace::autoclean" as a pragma?


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
    use Package::Stash ();
    use PPI::Document ();
    use Set::Object ();
    use Symbol ();
    
    
    my %exported_symbols_per_package;
    
    
    sub analyze {
        my ($class, $input, $handler) = @ARG;
        my $document = PPI::Document->new($input);
        my $included_modules = Set::Object->new;
        my @tokens = $class->_list_tokens($document);
        my @defects;
        
        $handler //= sub {
            my ($defect, $include) = @ARG;
            push @defects, {$defect => $include};
        };
        
        INCLUDE:
        foreach my $include ($class->_list_includes($document)) {
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
    
    
    sub _create_symbol {
        return substr ${Symbol::gensym()}, 1;
    }
    
    
    sub _create_package {
        my ($class, $source_code) = @ARG;
        my $package_name = $class->_create_symbol;
        
        eval "package $package_name;\n$source_code\n1;" or die $EVAL_ERROR;
        return $package_name;
    }
    
    
    sub _list_includes {
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
    
    
    sub _list_package_exports {
        my ($class, $package_name) = @ARG;
        
        return $exported_symbols_per_package{$package_name} // do {
            my $stash = Package::Stash->new(
                $class->_create_package("use $package_name;"));
            
            Set::Object->new(grep {$ARG ne 'BEGIN'} $stash->list_all_symbols);
        };
    }
    
    
    sub _list_tokens {
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
        my ($doc, $defect) = Includes->analyze(\'use Carp (); Carp:;');
        ok(exists $defect->{unused});
    }
    
    
    sub use_module_name : Test(2) {
        my ($doc, @defects) = Includes->analyze(\'use Carp (); %Carp::;');
        is(scalar(@defects), 0, 'use module namespace');
        
        ($doc, @defects) = Includes->analyze(\'use Carp (); Carp::;');
        is(scalar(@defects), 0, 'use module literal');
    }
    
    
    sub use_module_scalar : Test(1) {
        my ($doc, @defects) = Includes->analyze(
            \'use Carp (); $Carp::Verbose = 1;');
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
