#!/usr/bin/env perl

use defaults;
use Browser::Application::Chrome::Windows ();
use Browser::Application::Firefox::Windows ();
use Browser::Application::Opera::Windows ();


my @browsers = (
    Browser::Application::Chrome::Windows->new->find,
    Browser::Application::Firefox::Windows->new->find,
    Browser::Application::Opera::Windows->new->find,
);


foreach my $browser (@browsers) {
    say $browser->version, ' -> ', $browser->path;
#     $browser->go_to('http://www.example.com');
}
