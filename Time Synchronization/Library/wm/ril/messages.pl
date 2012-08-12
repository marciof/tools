#!/usr/bin/perl

# Extracts errors messages.

use defaults;


my $messages = 'messages';
open my $impl, '>', "$messages.cpp";
open my $interface, '>', "$messages.h";

print $impl (<< "C++");
#include "$messages.h"


static const TCHAR* _messages[] = {
    NULL,
C++

while (my $line = <STDIN>) {
    if ($line =~ m/(RIL_E_\w+)[^\@]+\@constdefine\s+(.+)$/) {
        my $constant = $1;
        my $text = ucfirst($2) . ($2 =~ m/\.$/ ? '' : '.');
        
        print $impl (<< "C++");
    TEXT("$text"), // $constant
C++
    }
}

print $impl (<< 'C++');
    NULL
};


namespace wm {
namespace ril {
    const TCHAR* GetErrorMessage(HRESULT result) {
        if (HRESULT_FACILITY(result) == FACILITY_RIL) {
            return _messages[HRESULT_CODE(result) & 0xFF];
        }
        else {
            return NULL;
        }
    }
}}
C++

print $interface (<< "C++");
#pragma once


#include "interface.h"


namespace wm {
namespace ril {
    const TCHAR* GetErrorMessage(HRESULT result);
}}
C++

close $impl;
close $interface;
