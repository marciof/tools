SetTitleMatchMode, 2
#If WinActive("ahk_class wxWindowClassNR") and WinActive(" - TodoPaper")
    Esc::return
    ^y::^+z
#If
