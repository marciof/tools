(XML
  (:h3 "Main Projects")
  
  (:dl
    (:dt "Alive Mail")
    (:dd (:a (@ (:href "http://alive-mail.sourceforge.net/")) "System")
         " for e-mail triage based on contextual social information.")
    
    (:dt "C Library")
    (:dd (:a (@ (:href "http://c-library.sourceforge.net/")) "Software library")
         " to ease development in the C programming language. "
         "I'm also using it to "
         (:a (@ (:href "Images/Bochs.png"))
             "learn more")
         " about µ-Kernels.")
    
    (:dt "LRDBi")
    (:dd "Web based interface, using "
         (:a (@ (:href "http://code.google.com/webtoolkit/")) "GWT")
         ", to a language resources database for "
         (:a (@ (:href "https://www.l2f.inesc-id.pt/")) "L²F INESC-ID")
         "."))
  
  (:h3 "Miscellaneous")
  
  (:dl
    (:dt "Algorithms")
    (:dd "Some "
         (:a (@ (:href "Portfolio/Algorithms.7z")) "algorithms")
         " made in Common Lisp, mainly used to verify my solutions for some of the exercises for the ASA course.")
    
    (:dt "CRC")
    (:dd "Implementation in D of some "
         (:a (@ (:href "Portfolio/CRC.d")) "CRC algorithms")
         " (CRC-32-IEEE 802.3, CRC-16-IBM, CRC-16-CCITT).")
    
    (:dt "Lispy")
    (:dd "Useful "
         (:a (@ (:href "Portfolio/Lispy.lisp")) "functions and macros")
         " for Common Lisp.")
    
    (:dt "Pearl")
    (:dd (:a (@ (:href "Portfolio/Pearl.pm")) "Perl module")
         " with some useful (at least for me) defaults and functions.")
    
    (:dt "RTP2 TV Guide")
    (:dd "RSS feed, "
         (:a (@ (:href "Portfolio/RTP2.cgi?view=source")) "written in Perl")
         ", with the daily "
         (:a (@ (:href "Portfolio/RTP2.cgi")) "TV guide for RTP2")
         ".")
    
    (:dt "Set Theory Shell")
    (:dd (:a (@ (:href "Portfolio/Set%20Theory%20Shell.7z")) "Interpreter")
         " of Set Theory operations written in Perl. Used to verify my solutions for some of the exercises for the QS course.")
    
    (:dt "macro")
    (:dd (:a (@ (:href "Portfolio/macro.lisp")) "First class macros")
         ", in Common Lisp, for interpreted code in "
         (:a (@ (:href "http://clisp.sourceforge.net/")) "CLISP")
         ".")
    
    (:dt "Reference")
    (:dd (:a (@ (:href "Portfolio/Reference.7z")) "Smart pointer")
         " implementation in C++ (similar to "
         (:a (@ (:href "http://www.boost.org/doc/libs/release/libs/smart_ptr"))
             "shared_ptr")
         ") that can be used as a simple Garbage Collector based on reference counting. I've used it extensively in an university project, and I didn't need a single explicit "
         (:tt "delete")
         " throughout the entire source code.")))
