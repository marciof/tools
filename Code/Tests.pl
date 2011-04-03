#!/usr/bin/env perl

use defaults;

# External modules:
use Mojolicious::Lite;

# Internal modules:
use JavaScript::File ();
use JavaScript::Package ();


my ($test_modules, $modules) = JavaScript::Package->new->test_suite;

foreach my $module (@$modules, @$test_modules) {
    get '/' . $module->file->path => sub {
        shift->render(text => $module->file->content);
    };
}

foreach my $module (@$test_modules) {
    get '/' . $module->file->name . '.html' => sub {
        shift->render('module', module => $module);
    };
}

foreach my $suffix (JavaScript::File->suffix, JavaScript::File->test_suffix) {
    $suffix =~ s/^\.//;
    app->types->type($suffix => 'application/javascript; charset=UTF-8');
}

get '/' => sub {
    shift->render('index', modules => $test_modules);
};

app->start;


__DATA__

@@ index.html.ep
% title 'Test';
% layout 'page';
% foreach my $module (@$modules) {
    <h2><a href="<%= $module->file->name %>.html"><%= $module->file->name %></a></h2>
    <iframe src="<%= $module->file->name %>.html"></iframe>
% }

@@ module.html.ep
% title $module->file->name;
% layout 'page';
<script src="test.js" type="text/javascript"></script>
% foreach my $dependency ($module->dependencies) {
<script src="<%= $dependency->file->path %>" type="text/javascript"></script>
% }
<script src="<%= $module->file->path %>" type="text/javascript"></script>

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
