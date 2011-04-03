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
    my @files = map {JavaScript::File->new(path => $ARG)}
        grep {!$ARG->is_dir() && ($ARG->basename =~ m/\Q$suffix\E$/)}
        $self->path->children(no_hidden => $true);
    
    my %files = map {($ARG->full_name => $ARG)} @files;
    my $dependencies = Graph::Directed->new;
    
    foreach my $file (@files) {
        foreach my $requirement ($file->requires) {
            $dependencies->add_edge($files{$requirement}, $file);
        }
        if ($file->is_test) {
            $dependencies->add_edge($files{$file->name}, $file);
        }
    }
    
    return $dependencies;
}


sub modules {
    my ($self) = @ARG;
    my $dependencies = $self->dependencies;
    my %modules;
    
    foreach my $file ($dependencies->topological_sort) {
        my @dependencies = map {$modules{$ARG->full_name}}
            $dependencies->all_predecessors($file);
        
        $modules{$file->full_name} = JavaScript::Module->new(
            dependencies => \@dependencies,
            file => $file);
    }
    
    return sort {@{$a->dependencies} <=> @{$b->dependencies}} values %modules;
}


sub test_suite {
    my ($self) = @ARG;
    my (@test_modules, @modules);
    
    foreach my $module ($self->modules) {
        if ($module->file->is_test) {
            push @test_modules, $module;
        }
        else {
            push @modules, $module;
        }
    }
    
    return (\@test_modules, \@modules);
}


1;
