#!/usr/bin/env perl
# TODO: Refactor into separate files.

package Script;

use defaults;
use File::Basename ();
use Moose;
use MooseX::Types::Path::Class;
use Regexp::Common qw(comment);


has path => (
    is => 'ro',
    isa => 'Path::Class::File',
    required => $true,
    coerce => $true,
);


# --- Class methods ---

sub suffix {
    return '.js';
}


sub test_suffix {
    my ($class) = @ARG;
    return '.test' . $class->suffix;
}


# --- Instance methods ---

sub content {
    my ($self) = @ARG;
    return scalar $self->path->slurp(iomode => '<:encoding(UTF-8)');
}


sub full_name {
    my ($self) = @ARG;
    return scalar File::Basename::fileparse($self->path, $self->suffix);
}


sub is_test {
    my ($self) = @ARG;
    my $suffix = $self->test_suffix;
    
    return $self->path->basename =~ m/\Q$suffix\E$/;
}


sub name {
    my ($self) = @ARG;
    return scalar File::Basename::fileparse($self->path,
        $self->test_suffix, $self->suffix);
}


sub requires {
    my ($self) = @ARG;
    my $comment_re = $Regexp::Common::RE{comment}{ECMAScript};
    my ($overview) = ($self->content =~ m/^($comment_re)/);
    my ($requires) = ($overview =~ m/\@requires \s+ (.+)/x);
    
    return split m/\s+/, ($requires // '');
}


package Module;

use defaults;
use Moose;


has dependencies => (
    is => 'ro',
    isa => 'ArrayRef[Module]',
    default => sub {[]},
    auto_deref => $true,
);

has implementation => (
    is => 'ro',
    isa => 'Script',
    required => $true,
);


package Package;

use defaults;
use File::Spec ();
use Graph::Directed ();
use Moose;
use MooseX::Types::Path::Class;


has path => (
    is => 'ro',
    isa => 'Path::Class::Dir',
    default => File::Spec->curdir,
    coerce => $true,
);


# --- Instance methods ---

sub dependencies {
    my ($self) = @ARG;
    my $suffix = Script->suffix;
    my @scripts = map {Script->new(path => $ARG)}
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
        
        $modules{$script->full_name} = Module->new(
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


package main;

use defaults;
use Mojolicious::Lite;


# TODO: Handle not found modules.
# TODO: Refactor module handling.
# TODO: Simplify content types.

my ($test_modules, $modules) = Package->new->test_suite;
my %modules = map {($ARG->implementation->name => $ARG)} @$modules;
my %test_modules = map {($ARG->implementation->name => $ARG)} @$test_modules;


get '/' => sub {
    my ($self) = @ARG;
    $self->render('index', modules => $test_modules);
};


get '/:module.html' => sub {
    my ($self) = @ARG;
    $self->render('module', module => $test_modules{$self->param('module')});
};


get '/:module' . Script->suffix => sub {
    my ($self) = @ARG;
    my $module = $modules{$self->param('module')};
    
    $self->render(text => $module->implementation->content);
};


get '/:module' . Script->test_suffix => sub {
    my ($self) = @ARG;
    my $module = $test_modules{$self->param('module')};
    
    $self->render(text => $module->implementation->content);
};


foreach my $suffix (Script->suffix, Script->test_suffix) {
    $suffix =~ s/^\.//;
    app->types->type($suffix => 'application/javascript; charset=UTF-8');
}

app->start;


__DATA__

@@ index.html.ep
% title 'Test';
% layout 'page';
% foreach my $module (@$modules) {
    <h2><a href="<%= $module->implementation->name %>.html"><%= $module->implementation->name %></a></h2>
    <iframe src="<%= $module->implementation->name %>.html"></iframe>
% }

@@ module.html.ep
% title $module->implementation->name;
% layout 'page';
<script src="test.js" type="text/javascript"></script>
% foreach my $dependency ($module->dependencies) {
<script src="<%= $dependency->implementation->path %>" type="text/javascript"></script>
% }
<script src="<%= $module->implementation->path %>" type="text/javascript"></script>

@@ layouts/page.html.ep
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
  <head>
    <title><%= title %></title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <style type="text/css">
iframe {
    height: 20em;
    width: 100%;
}
    </style>
  </head>
  <body>
    <%= content %>
  </body>
</html>

@@ test.js
function test(label, tests) {
    var numberTests = 0;
    var failures = [];
    
    if (arguments.length == 1) {
        tests = label;
        label = undefined;
    }
    
    for (var name in tests) {
        try {
            ++numberTests;
            tests[name]();
        }
        catch (exception) {
            failures[failures.length] = {exception: exception, name: name};
        }
    }
    
    var successes = numberTests - failures.length;
    
    if (label) {
        document.write('<h4>' + label + '</h4>');
    }
    
    if (successes > 0) {
        document.write('<p>Successes: ' + successes + '</p>');
    }
    
    if (failures.length > 0) {
        document.write('<p>Failures: ' + failures.length + '</p>');
        document.write('<ul>');
        
        for (var i = 0; i < failures.length; ++i) {
            var what = failures[i].name;
            var why = failures[i].exception.message;
            
            document.write('<li><em>' + what + '</em>: <q>' + why + '</q></li>');
        }
        
        document.write('</ul>');
    }
}
