Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Change to the script directory
WshShell.CurrentDirectory = scriptDir

' Launch Python script silently (no console window)
WshShell.Run "py veleron_voice_flow.py", 0, False

' If py fails, try python
If Err.Number <> 0 Then
    WshShell.Run "python veleron_voice_flow.py", 0, False
End If
