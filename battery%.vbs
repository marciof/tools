' Shortcut this in location `shell:startup`.

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

ScriptFolder = FSO.GetParentFolderName(WScript.ScriptFullName)
PSPath = ScriptFolder & "\battery%.ps1"

WshShell.Run "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -NoProfile -File """ & PSPath & """", 0, False
