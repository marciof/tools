#!/usr/bin/env perl

# TODO: Split into files.

use defaults;

# External modules:
use Mojo::Server::Daemon ();
use Mojolicious::Lite;

# Internal modules:
use JavaScript::File ();
use JavaScript::Package ();


my $test_suite = JavaScript::Package->new->test_suite;
my $daemon = Mojo::Server::Daemon->new(app => app);
my $auto_route = 'auto';

get '/:type' => [type => qr/(?: \Q$auto_route\E) ?/x] => {type => ''} => sub {
    my ($self) = @ARG;
    
    $self->render('index',
        type => $self->param('type'),
        modules => scalar $test_suite->tests);
};

foreach my $suffix (JavaScript::File->suffixes) {
    $suffix =~ s/^\.//;
    app->types->type($suffix => 'application/javascript; charset=UTF-8');
}

foreach my $module ($test_suite->modules) {
    get '/' . $module->file->path => sub {
        shift->render(text => $module->file->content);
    };
}

foreach my $module ($test_suite->tests) {
    foreach my $auto ($false, $true) {
        my $prefix = $auto ? $auto_route : '';
        my $route = $prefix . '/' . $module->file->name . '.html';
        
        get $route => sub {
            my ($self) = @ARG;
            
            $self->render('module',
                auto => $auto,
                module => $module);
        };
    }
}

my %remaining_tests = map {($ARG->file->name => $true)} $test_suite->tests;
my $timeout = 1;

get '/done/:module' => sub {
    my ($self) = @ARG;
    
    delete $remaining_tests{$self->param('module')};
    $self->render_static('done.gif');
    
    unless (%remaining_tests) {
        $self->on_finish(sub {
            $daemon->ioloop->timer($timeout, sub {
                $daemon->ioloop->stop;
            });
        });
    }
};

get '/failure/:module/:test' => sub {
    my ($self) = @ARG;
    my ($module, $test) = ($self->param('module'), $self->param('test'));
    
    say $module, '.', $test, ': ', $self->param('reason');
    $self->render_static('done.gif');
};

app->log->level('info');
$daemon->ioloop->accept_timeout($timeout);
$daemon->ioloop->connect_timeout($timeout);
$daemon->run;


__DATA__

@@ index.html.ep
% title 'Tests';
% layout 'page';
% foreach my $module (@$modules) {
%   my $url = $type . '/' . $module->file->name . '.html';
    <h2><a href="<%= $url %>"><%= $module->file->name %></a></h2>
    <iframe class="Test" src="<%= $url %>"></iframe>
% }

@@ module.html.ep
% title $module->file->name;
% layout 'page';
    <script src="/test.js" type="text/javascript"></script>
    <script type="text/javascript">
test.auto = <%= $auto ? 'true' : 'false' %>;
test.module = '<%= $module->file->name %>';
    </script>
% foreach my $dependency ($module->dependencies) {
    <script src="/<%= $dependency->file->path %>" type="text/javascript"></script>
% }
    <script src="/<%= $module->file->path %>" type="text/javascript"></script>

@@ layouts/page.html.ep
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
  <head>
    <title><%= title %></title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <style type="text/css">
.Result {
    height: 0;
    position: absolute;
}
.Test {
    height: 20em;
    width: 100%;
}
    </style>
  </head>
  <body>
    <%= content %>
  </body>
</html>

@@ done.gif (base64)
R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==

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
            test.failure(name, exception.message);
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
    
    test.done();
}

test.done = function() {
    test.reply('/done/' + encodeURIComponent(test.module));
};

test.failure = function(name, reason) {
    test.reply('/failure'
        + '/' + encodeURIComponent(test.module)
        + '/' + encodeURIComponent(name)
        + '?reason=' + encodeURIComponent(reason));
};

test.reply = function(url) {
    if (test.auto) {
        document.write('<div class="Result"><img src="'
            + url + '" alt=""/></div>');
    }
};
