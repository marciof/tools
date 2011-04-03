package JavaScript::Package;

use defaults;

# External modules:
use File::Spec ();
use Graph::Directed ();
use Moose;
use MooseX::Types::Path::Class;

# Internal modules:
use JavaScript::File ();
use JavaScript::Module ();


has path => (
    is => 'ro',
    isa => 'Path::Class::Dir',
    default => File::Spec->curdir,
    coerce => $true,
);


# --- Instance methods ---

sub dependencies {
    my ($self) = @ARG;
    my $suffix = JavaScript::File->suffix;
    my @scripts = map {JavaScript::File->new(path => $ARG)}
        grep {!$ARG->is_dir() && ($ARG->basename =~ m/\Q$suffix\E$/)}
        $self->path->children(no_hidden => $true);
    
    my %scripts = map {($ARG->full_name => $ARG)} @scripts;
    my $dependencies = Graph::Directed->new;
    
    foreach my $script (values %scripts) {
        foreach my $requirement ($script->requires) {
            $dependencies->add_edge($scripts{$requirement}, $script);
        }
        if ($script->is_test) {
            $dependencies->add_edge($scripts{$script->name}, $script);
        }
    }
    
    return $dependencies;
}


sub modules {
    my ($self) = @ARG;
    my $dependencies = $self->dependencies;
    my %modules;
    
    foreach my $script ($dependencies->topological_sort) {
        my @dependencies = map {$modules{$ARG->full_name}}
            $dependencies->all_predecessors($script);
        
        $modules{$script->full_name} = JavaScript::Module->new(
            dependencies => \@dependencies,
            implementation => $script);
    }
    
    return sort {@{$a->dependencies} <=> @{$b->dependencies}} values %modules;
}


sub test_suite {
    my ($self) = @ARG;
    my (@test_modules, @modules);
    
    foreach my $module ($self->modules) {
        if ($module->implementation->is_test) {
            push @test_modules, $module;
        }
        else {
            push @modules, $module;
        }
    }
    
    return (\@test_modules, \@modules);
}


1;
