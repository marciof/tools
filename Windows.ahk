; https://autohotkey.com/board/topic/22194-vista-explorer-backspace-for-parent-folder-as-in-xp/

#If WinActive("ahk_class CabinetWClass")
    Backspace::
        ControlGet, renameStatus, Visible,, Edit1, A
        ControlGetFocus focussedControl, A
        
        inExplorer := ((renameStatus != 1)
            && ((focussedControl == "DirectUIHWND3")
                || (focussedControl == "SysTreeView321")))
        
        if  (inExplorer) {
            SendInput {Alt down}{Up}{Alt up}
        }
        else {
            Send {Backspace}
        }
    return
#If
