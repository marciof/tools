#!/usr/bin/env perl

use forks;

use strict;
use utf8;
use warnings;

use Daemon::Generic ();
use English '-no_match_vars';
use Errno ();
use Fcntl ();
use File::Basename ();
use File::Spec ();
use Git ();
use Path::Class ();
use POSIX ();
use Try::Tiny;


my $COMMIT_TEMPLATE_FILE = 'COMMIT_TEMPLATE_MSG';
my $COMMIT_TEMPLATE_OPTION = 'commit.template';
my $GIT_OPTION = 'git';


sub add_ticket_number {
    my ($self, $git, $commit_message) = @ARG;
    my $local_branch = eval {$git->command_oneline(qw(symbolic-ref HEAD))};
    
    my $remote_branch = eval {
        $git->command_oneline(
            qw{for-each-ref --format=%(upstream:short)},
            $local_branch);
    };
    
    foreach my $branch ($remote_branch, $local_branch) {
        if (my ($ticket) = (($branch // '') =~ m/(\w+-\d+)/)) {
            print $commit_message "[\U$ticket\E] ";
            last;
        }
    }
    
    print $commit_message "\n";
    return;
}


sub gd_flags_more {
    return ("--$GIT_OPTION path" => 'Git repository path.');
}


sub gd_preconfig {
    my ($self) = @ARG;
    my $config_file = $self->get_config_file;
    my $pid_file = $self->get_pid_file;
    my %config;
    
    push @{$self->{git_repos}}, eval {$config_file->slurp(chomp => 1)};
    
    # Allow execution by non-root users.
    if ($EFFECTIVE_USER_ID != 0) {
        my $tmp_dir = Path::Class::dir(File::Spec->tmpdir);
        $config{pidfile} = $tmp_dir->file($pid_file->basename)->stringify;
    }
    
    return %config;
}


sub gd_more_opt {
    my ($self) = @ARG;
    return ($GIT_OPTION . '=s@' => \$self->{git_repos});
}


sub gd_quit_event {
    my ($self) = @ARG;
    return;
}


sub gd_run {
    my ($self) = @ARG;
    
    foreach my $git ($self->list_git_repos) {
        print 'Tracking: ', $git->wc_path, "\n";
        my ($template_file, $cleanup) = $self->get_template_file($git);
        
        async {
            try {
                while (1) {
                    my $commit_message = $template_file->openw;
                    
                    print 'Template: ', $git->wc_path, "\n";
                    $self->add_ticket_number($git, $commit_message);
                    close $commit_message;
                }
            }
            catch {
                die $ERRNO if $ERRNO != Errno::EINTR;
            };
            
            print 'Cleaning up: ', $git->wc_path, "\n";
            $cleanup->();
        };
    }
    
    print "Waiting...\n";
    wait;
    return;
}


sub get_config_file {
    my ($self) = @ARG;
    return Path::Class::file($self->{configfile});
}


sub get_pid_file {
    my ($self) = @ARG;
    return Path::Class::file($self->{gd_pidfile});
}


sub get_template_file {
    my ($self, $git) = @ARG;
    my $template_file = $git->config($COMMIT_TEMPLATE_OPTION);
    
    if (defined $template_file) {
        $template_file = Path::Class::file($template_file);
    }
    else {
        my $git_dir = Path::Class::dir($git->repo_path);
        $template_file = $git_dir->file($COMMIT_TEMPLATE_FILE);
        
        $git->command_noisy('config',
            $COMMIT_TEMPLATE_OPTION, $template_file);
    }
    
    $template_file->remove;
    
    POSIX::mkfifo($template_file,
        Fcntl::S_IRUSR + Fcntl::S_IWUSR + Fcntl::S_IRGRP + Fcntl::S_IROTH);
    
    return ($template_file, sub {
        $template_file->remove;
        $template_file->touch;
        return;
    });
}


sub list_git_repos {
    my ($self) = @ARG;
    my @paths = @{$self->{git_repos} // []};
    my @git;

    foreach my $path (@paths > 0 ? @paths : Path::Class::dir) {
        try {
            push @git, Git->repository($path);
        }
        catch {
            warn $ARG;
        };
    }

    foreach my $git (@git) {
        my $sub_modules = eval {
            $git->command('config',
                '--null',
                '--file' => '.gitmodules',
                '--get-regexp' => '^submodule\.\w+\.path$')
        } // next;
        
        my $path = Path::Class::dir($git->wc_path);
        my @sub_modules = map {[split /\n/]->[-1]} split /\0/, $sub_modules;
        
        push @git, map {Git->repository($path->subdir($ARG))} @sub_modules;
    }
    
    return @git;
}


Daemon::Generic::newdaemon(
    progname => File::Basename::fileparse(
        Path::Class::file($PROGRAM_NAME)->resolve, qr/\.\w+$/));
