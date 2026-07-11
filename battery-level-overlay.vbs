' Shortcut this in location `shell:startup`.

Option Explicit

' https://learn.microsoft.com/previous-versions/windows/internet-explorer/ie-developer/windows-scripting/ahcz2kh6(v=vs.84)
Dim Shell: Set Shell = CreateObject("WScript.Shell")

' https://learn.microsoft.com/office/vba/language/reference/user-interface-help/filesystemobject-object
Dim FS: Set FS = CreateObject("Scripting.FileSystemObject")

' https://learn.microsoft.com/previous-versions/windows/internet-explorer/ie-developer/windows-scripting/at5ydy31(v=vs.84)
Dim scriptPath: scriptPath = FS.BuildPath( _
    FS.GetParentFolderName(WScript.ScriptFullName), _
    FS.GetBaseName(WScript.ScriptFullName) & ".ps1")

If Not FS.FileExists(scriptPath) Then
    ' https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/msgbox-function
    MsgBox _
		"Not found:" & vbCrLf & scriptPath, _
		vbExclamation, _
		"Battery Level Overlay"
    WScript.Quit
End If

' https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_powershell_exe
Dim powerShellCmd: powerShellCmd = "powershell.exe " _
    & "-WindowStyle Hidden " _
    & "-ExecutionPolicy Bypass " _
    & "-NoProfile " _
    & "-File """ & scriptPath & """"

' https://learn.microsoft.com/previous-versions/windows/internet-explorer/ie-developer/windows-scripting/d5fk67ky(v=vs.84)
Const WINDOW_STYLE_HIDE = 0
Const DONT_WAIT_ON_RETURN = False
Shell.Run powerShellCmd, WINDOW_STYLE_HIDE, DONT_WAIT_ON_RETURN
