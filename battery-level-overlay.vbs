' Shortcut this in location `shell:startup`.

Option Explicit

Dim Shell: Set Shell = CreateObject("WScript.Shell")

' https://learn.microsoft.com/office/vba/language/reference/user-interface-help/filesystemobject-object
Dim FS: Set FS = CreateObject("Scripting.FileSystemObject")

' https://learn.microsoft.com/office/vba/language/reference/user-interface-help/getparentfoldername-method
Dim folderName: folderName = FS.GetParentFolderName(WScript.ScriptFullName)

' https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_powershell_exe
Dim pwshCmd: pwshCmd = "powershell.exe " _
    & "-WindowStyle Hidden " _
    & "-ExecutionPolicy Bypass " _
    & "-NoProfile " _
    & "-File """ & folderName & "\battery-level-overlay.ps1" & """"

Const WINDOW_STYLE_HIDE = 0
Const DONT_WAIT_ON_RETURN = False
Shell.Run pwshCmd, WINDOW_STYLE_HIDE, DONT_WAIT_ON_RETURN
