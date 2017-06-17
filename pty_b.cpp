/*
This example is public domain. Use as you see fit.

The purpose of this example is show how a process can run a shell transparently and be able to filter it's input and output.
This example does not show off any I/O filtering, it only provides the framework on which that could be added.

Tested only on GNU/Linux with recent kernels and recent g++ and clang++

This example is based on original found here:
https://www.scriptjunkie.us/wp-content/uploads/2011/04/stdioterminallogger.c

There were 2 problems with the code this example was based on.
1) Terminal (re)sizing was not being handled
2) Some applications display incorrectly or keys don't work
   a) with 'joe', Enter, Ctrl-M, and Ctrl-J don't work
   b) 'joe' has display isues
   c) 'snake' (game) has display issues

Also, be aware of this:
    #define LOGFILELOCATION "/tmp/.shlog"
in the original code, not this example.

This example does not write produce any files. (intermediate or otherwise)


The following programs do seem to work correctly:
vi, vim, nano, mcedit, htop, top

#1 has been solved with a resize handler (see handler and handleTerminalResize)


Use this in shell's profile/bashrc to indicate pty-filter is present
[ "${inptyfilter}" == "true" ] && PS1="(pty-filter) ${PS1}"

Compile with any of the following:

g++ -std=c++11 pty-filter.cpp  -lutil -o pty-filter
g++ -std=c++1y pty-filter.cpp  -lutil -o pty-filter
g++ -std=c++1z pty-filter.cpp  -lutil -o pty-filter
clang++ -std=c++11 pty-filter.cpp  -lutil -o pty-filter
clang++ -std=c++1y pty-filter.cpp  -lutil -o pty-filter
clang++ -std=c++1z pty-filter.cpp  -lutil -o pty-filter

# for stricter compilation:
clang++ -std=c++1z pty-filter.cpp -lutil -o pty-filter -Wall -Werror -Weverything -Wno-c++98-compat -Wno-missing-prototypes -Wno-disabled-macro-expansion -Wno-vla-extension -Wno-vla

*/

// standard C stuff
#include <cstdio>
#include <cstdlib>
#include <csignal>
#include <cerrno>
#include <cstdarg>

// C++ stuff
#include <string>

// Everything else
#include <pty.h>
#include <unistd.h>
#include <termios.h>
#include <sys/mman.h>
#include <sys/wait.h>

// shared globals
struct sharedBookT {
    pid_t childPid;
    pid_t parentPid;
    pid_t shellPid;
    int shellFd;
    termios oldTerm, newTerm, shellTerm;
    bool readyToQuit;
    char fromTerminalBuffer [4096];
    char toTerminalBuffer [4096];
    char padding [3];
};


// avoid non C++ casts (when used with stricter compilation)
typedef const char* constCharPtrT;
typedef void* voidPtr;
typedef sharedBookT* sharedBookPtrT;

static sharedBookPtrT sharedBookPtr = 0;

// sprintf for std::string
std::string Sprintf (const char* fmt, ...) __attribute__ ((format (printf, 1, 2)));
std::string Sprintf (const char* fmt, ...) {
    va_list ap;
    va_start (ap, fmt);
    const auto n = vsnprintf (0, 0, fmt, ap);
    va_end (ap);

    char result [n+2];

    va_start (ap, fmt);
    vsnprintf (result, size_t (n+1), fmt, ap);
    va_end (ap);

    return std::string (result);
}

// c_str and length shortcut operators for std::string
const char* operator* (const std::string& s) { return s.c_str (); }
size_t operator+ (const std::string& s) { return s.length (); }

// resize shell's pty and notifiy chell of change
void handleTerminalResize () {
    sharedBookT& shared = *sharedBookPtr;
    winsize ws;
    ioctl(0, TIOCGWINSZ, &ws);
    ioctl(shared.shellFd, TIOCSWINSZ, &ws);
    sigqueue (shared.shellPid, SIGWINCH, {0});
}

// log signal, for convience just to stdout
void logsignal (int signal) {
    // can't reliably use regular printf from a signal handler
    const auto msg = Sprintf ("Got signal %d\n", signal);
    write (1, *msg, +msg);
}

// common signal handler
void handler(int signal, siginfo_t * infoP, void *context __attribute__ ((unused))) {
    const auto& si = *infoP;
    const auto myPid = getpid ();

    sharedBookT& shared = *sharedBookPtr;

    // using SIGUSR to notify processes of termination
    // (processes must check for it after blocking syscalls)
    if (signal == SIGUSR2) { // Notification to quit
        shared.readyToQuit = true;
        return;
    }

    auto cc = char (-1);
    if (myPid == shared.parentPid) {
        // only parent process should handle these
        // if child processes handle these as well, there are multiple insertions
        switch (si.si_signo) {
            case SIGINT: cc = 0x03; break;  // "Ctrl-C"
            case SIGTSTP: cc = 0x1A; break; // "Ctrl-Z"
            case SIGQUIT: cc = 0x1C; break; // "Ctrl-\"
            case SIGWINCH: handleTerminalResize (); break;
            default: logsignal (signal); break;
        }
    }
    // write control character (if any) to shell's pty
    if (-1 < cc) write(shared.shellFd, &cc, 1);
}

// Add common signal handler for each signal
void setupsignal(int signal) {
    struct sigaction act;
    sigaction(signal, NULL, &act);
    act.sa_sigaction = handler;
    act.sa_flags |= SA_SIGINFO;
    sigaction(signal, &act, NULL);
}

// launch shell with new pty
void launchShell(char* argv[]) {
    sharedBookT& shared = *sharedBookPtr;
    tcgetattr(0, &shared.shellTerm);

    const auto pid = forkpty(&shared.shellFd, NULL, &shared.shellTerm, NULL);
    if (pid == -1 || pid == 0) {
        if (pid == 0) {
            shared.shellPid = getpid ();
            // inform shell it's pty is being filtered
            setenv ("inptyfilter", "true", 1);
            exit(execvp(argv[0], argv));
        }
        else {
            perror ("forkpty failed");
            exit (1);
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc <= 1) {
        return EXIT_FAILURE;
    }

    // create shared globals structure
    sharedBookPtr = sharedBookPtrT (mmap (
        NULL, sizeof (sharedBookT),
        PROT_READ | PROT_WRITE,
        MAP_SHARED | MAP_ANONYMOUS, -1, 0
    ));

    sharedBookT& shared = *sharedBookPtr;

    launchShell(argv + 1);
    shared.parentPid = getpid ();

    //Set up handler for signals
    setupsignal(SIGINT);
    setupsignal(SIGTSTP);
    setupsignal(SIGUSR1);
    setupsignal(SIGUSR2);
    setupsignal(SIGQUIT);
    setupsignal(SIGWINCH);
    //setupsignal(SIGTTIN);
    //setupsignal(SIGTTOU);

    // fork to handle output to the terminal
    if (0 == fork ()) {
        shared.childPid = getpid ();

        // loop while reading and echoing the pty's output
        for (;;) {
            // read from Shell's Pty
            const auto charsRead = read (shared.shellFd, shared.toTerminalBuffer, sizeof (shared.toTerminalBuffer));

            // if characters were read, echo them and continue
            if (0 < charsRead) {
                write (1, shared.toTerminalBuffer, size_t (charsRead));
                continue;
            }

            // if error, check if we are done            
            if ((charsRead == -1) and (errno == EIO)) {
                fprintf (stderr, "\nterminating I/O processes\r\n");
                // signal parent to exit
                sigqueue (shared.parentPid, SIGUSR2, {0});
                break;
            }
        }

        fprintf (stderr, "Exiting pty-filter (toTerminal)\r\n");
        exit (0);
    }

    // wait for pids to be updated
    while ((0 == shared.shellPid) or (0 == shared.childPid)) usleep (1);

    fprintf (stderr, "parent: %d\n", shared.parentPid);
    fprintf (stderr, "shell: %d\n", shared.shellPid);
    fprintf (stderr, "child: %d\n", shared.childPid);

    tcgetattr(0, &shared.oldTerm); // Disable buffered I/O and echo mode for pty
    shared.newTerm = shared.oldTerm;
    cfmakeraw (&shared.newTerm);
    tcsetattr(0, TCSANOW, &shared.newTerm);

    // shell needs intial sizing
    handleTerminalResize ();

    for (;;) {//loop while processing input from pty
        const auto charsRead = read (0, shared.fromTerminalBuffer, sizeof (shared.fromTerminalBuffer));
        // SIGUSR1 will drop process out of read so flag can be read
        if (shared.readyToQuit) {
            fprintf (stderr, "Exiting pty-filter (fromTerminal)\r\n");
            break;
        }

        // in we got input from the terminal, pass it on to the shell's pty
        if (0 < charsRead) {
            write (shared.shellFd, shared.fromTerminalBuffer, size_t (charsRead));
            continue;
        }

        // if error check if we are done
        // However, this is never executed, child fork terminates first
        if ((charsRead == -1) and (errno == EIO)) break;
    }

    tcsetattr(0, TCSANOW, &shared.oldTerm); //reset terminal

    // wait for child forks to exit
    for (;;) {
        auto wpid = wait (0);
        if (wpid == -1) break;
        fprintf (stderr, "%d is done\n", wpid);
    }
    perror ("status");
    return 0;
}
