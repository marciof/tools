#!/usr/bin/perl

# Extracts errors messages.

use strict;
use warnings;


my $messages = 'messages';

open my $ril, '<', 'ril.h' or die $!;
open my $impl, '>', "$messages.cpp" or die $!;
open my $interface, '>', "$messages.h" or die $!;

print $impl (<< "EOT");
#include "$messages.h"


static const TCHAR* _messages[] = {
    NULL,
EOT

while (my $line = <$ril>) {
    if ($line =~ m/(RIL_E_\w+)[^\@]+\@constdefine\s+(.+)$/) {
        my $constant = $1;
        my $text = ucfirst($2).($2 =~ m/\.$/ ? '' : '.');
        
        print $impl (<< "EOT");
    TEXT("$text"), // $constant
EOT
    }
}

print $impl (<< 'EOT');
    NULL
};


namespace Wm {
namespace Api {
namespace Ril {
    const TCHAR* LoadErrorMessage(HRESULT result) {
        if (HRESULT_FACILITY(result) == FACILITY_RIL) {
            return _messages[HRESULT_CODE(result) & 0xFF];
        }
        else {
            return NULL;
        }
    }
}}}
EOT

print $interface (<< "EOT");
#pragma once


#include "wrapper.h"


namespace Wm {
namespace Api {
namespace Ril {
    const TCHAR* LoadErrorMessage(HRESULT result);
}}}
EOT

close $ril;
close $impl;
close $interface;