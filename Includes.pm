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
        
        return ($self eq $module)
            || (($self =~ /^ \Q$module\E (::\w+) $/x)
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
        
        return;
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


use defaults;

unless (caller) {
    die "Usage: file\n" if @ARGV == 0;
    
    Includes->analyze($ARGV[0], sub {
        my ($defect, $include) = @ARG;
        
        printf "%s %s at line %d.\n",
            ucfirst($defect), $include->module, $include->line_number;
    });
}


1;
