// Standard
#include <iostream>

// External
#include <pstreams/pstream.h>


int main() {
    redi::ipstream in("ls");
    std::string str;

    while (in >> str) {
        std::cout << str << std::endl;
    }
}
