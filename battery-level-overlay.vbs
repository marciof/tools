' Shortcut this in location `shell:startup`.

Option Explicit

' https://learn.microsoft.com/previous-versions/windows/internet-explorer/ie-developer/windows-scripting/ahcz2kh6(v=vs.84)
Dim Shell: Set Shell = CreateObject("WScript.Shell")

' https://learn.microsoft.com/office/vba/language/reference/user-interface-help/filesystemobject-object
Dim FS: Set FS = CreateObject("Scripting.FileSystemObject")

' https://learn.microsoft.com/previous-versions/windows/internet-explorer/ie-developer/windows-scripting/at5ydy31(v=vs.84)
Dim folderName: folderName = FS.GetParentFolderName(WScript.ScriptFullName)
Dim baseName: baseName = FS.GetBaseName(WScript.ScriptFullName)

' https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_powershell_exe
Dim pwshCmd: pwshCmd = "powershell.exe " _
    & "-WindowStyle Hidden " _
    & "-ExecutionPolicy Bypass " _
    & "-NoProfile " _
    & "-File """ & FS.BuildPath(folderName, baseName & ".ps1") & """"

' https://learn.microsoft.com/previous-versions/windows/internet-explorer/ie-developer/windows-scripting/d5fk67ky(v=vs.84)
Const WINDOW_STYLE_HIDE = 0
Const DONT_WAIT_ON_RETURN = False
Shell.Run pwshCmd, WINDOW_STYLE_HIDE, DONT_WAIT_ON_RETURN
