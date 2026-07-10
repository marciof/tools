/*
 * Show battery level percentage on the bottom right of the screen.
 * Hides on mouse over.
 */


#Requires AutoHotkey v2.0
#SingleInstance Force
#Warn


; See https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setthreaddpiawarenesscontext
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 := -4

; See https://learn.microsoft.com/windows/win32/winmsg/extended-window-styles
WS_EX_TRANSPARENT := '0x00000020'

; See https://learn.microsoft.com/windows/win32/api/winbase/ns-winbase-system_power_status
SIZEOF_SYSTEM_POWER_STATUS := 1 + 1 + 1 + 1 + 4 + 4
BATTERY_LIFE_PERCENT_BYTE_OFFSET := 0 + 1 + 1
BATTERY_LIFE_PERCENT_TYPE := 'UChar'

; See https://www.autohotkey.com/docs/v2/lib/WinSetTransColor.htm
FULL_TRANSPARENCY_LEVEL := 255


transparencyColor := 'Black'
fontColor := 'White'
fontName := 'Arial'

updateFreqSecs := 10
mouseOverCheckFreqMillis := 200
mouseOverMargin := 100

boxLeft := 0
boxRight := 0
boxTop := 0
boxBottom := 0

isHidden := true

xPos := 0
yPos := 0
offsetRight := 3
offsetBottom := 10


; See https://www.autohotkey.com/docs/v2/misc/DPIScaling.htm
DllCall('SetThreadDpiAwarenessContext',
    'Ptr', DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)

; See https://www.autohotkey.com/docs/v2/lib/Gui.htm#Opt
global appGui := Gui(Format('+AlwaysOnTop -Caption +ToolWindow +DPIScale +E{1}',
    WS_EX_TRANSPARENT))

; Remove margins to prevent clipping.
appGui.MarginX := 0
appGui.MarginY := 0
appGui.BackColor := transparencyColor

; See https://www.autohotkey.com/docs/v2/lib/Gui.htm#SetFont
appGui.SetFont('q5 s14 c' . fontColor, fontName)

global textGui := appGui.Add('Text', 'w120 Center', formatBatteryLevel())

; See https://www.autohotkey.com/docs/v2/lib/WinSetTransColor.htm
WinSetTransColor(transparencyColor . ' ' . FULL_TRANSPARENCY_LEVEL, appGui)


calculatePosition()
showBatteryLevel()
updateBatteryLevel()

SetTimer(updateBatteryLevel, updateFreqSecs * 1000)
SetTimer(checkMouseOver, mouseOverCheckFreqMillis)


formatBatteryLevel(level := '') {
    return (level ? level . '%' : '--%')
}


calculatePosition() {
    global

    isHidden := true
    appGui.Show('Hide')

    local width, height
    appGui.GetPos(,, &width, &height)

    ; See https://www.autohotkey.com/docs/v2/lib/MonitorGetWorkArea.htm
    local wAreaRight, wAreaBottom
    MonitorGetWorkArea(,,, &wAreaRight, &wAreaBottom)

    xPos := wAreaRight - width - offsetRight
    yPos := wAreaBottom - height - offsetBottom

    boxLeft := xPos - mouseOverMargin
    boxRight := xPos + width + mouseOverMargin
    boxTop := yPos - mouseOverMargin
    boxBottom := yPos + height + mouseOverMargin

    isHidden := false
}


showBatteryLevel() {
    global

    ; See https://www.autohotkey.com/docs/v2/lib/Gui.htm#Show
    appGui.Show(Format('AutoSize NoActivate x{1} y{2}', xPos, yPos))
    isHidden := false
}


updateBatteryLevel() {
    global
    local powerStatus := Buffer(SIZEOF_SYSTEM_POWER_STATUS, 0)

    ; See https://learn.microsoft.com/windows/win32/api/winbase/nf-winbase-getsystempowerstatus
    if DllCall('kernel32.dll\GetSystemPowerStatus', 'Ptr', powerStatus) {
        textGui.Value := formatBatteryLevel(NumGet(
            powerStatus,
            BATTERY_LIFE_PERCENT_BYTE_OFFSET,
            BATTERY_LIFE_PERCENT_TYPE))
    }
    else {
        textGui.Value := formatBatteryLevel()
    }
}


checkMouseOver() {
    global
    local mouseX, mouseY

    CoordMode('Mouse', 'Screen')
    MouseGetPos(&mouseX, &mouseY)

    local isHovering := (
        mouseX >= boxLeft
        && mouseX <= boxRight
        && mouseY >= boxTop
        && mouseY <= boxBottom)

    if (isHovering && !isHidden) {
        appGui.Hide()
        isHidden := true
    }
    else if (!isHovering && isHidden) {
        showBatteryLevel()
    }
}
