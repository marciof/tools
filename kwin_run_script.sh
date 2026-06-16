#!/bin/sh

# Arguments: <file>

set -o errexit -o nounset

kwin_qdbus() {
    qdbus6 org.kde.KWin "$@"
}

# Arguments: <path> <name>
# Stdout: ID
kwin_load_script_by_name() {
    kwin_qdbus /Scripting loadScript "$@" \
        | grep --invert-match --max-count 1 --fixed-strings --regexp '-1'
}

# Arguments: <name>
kwin_unload_script_by_name() {
    kwin_qdbus /Scripting unloadScript "$@" \
        | grep --silent --fixed-strings --regexp true --regexp false
}

# Arguments: <path> <name>
# Stdout: ID
kwin_reload_script_by_name() {
    kwin_unload_script_by_name "$2"
    kwin_load_script_by_name "$1" "$2"
}

# Arguments: <ID>
kwin_run_script_by_id() {
    kwin_qdbus "/Scripting/Script$1" org.kde.kwin.Script.run
}

script_path="$(realpath "$1")"
script_name="$(basename "$script_path")"
script_id="$(kwin_reload_script_by_name "$script_path" "$script_name")"

kwin_run_script_by_id "$script_id"

# FIXME unload script properly
# FIXME use case with commands + journalctl + entr

# https://develop.kde.org/docs/plasma/kwin/
# https://develop.kde.org/docs/plasma/kwin/api/
# https://invent.kde.org/plasma/knighttime
# https://github.com/DefendTheDisabled/KDE-night-light-dimming
# https://invent.kde.org/plasma/powerdevil/-/blob/master/daemon/dbus/org.kde.ScreenBrightness.Display.xml?ref_type=heads

# org.kde.kwin.Script.stop

# journalctl --user -u plasma-kwin_wayland.service -g "js:" -f
# echo auto-screen-brightness.js | entr ./kwin_run_script.sh auto-screen-brightness.js

# "lower brightness by a regular step" + "non-silent mode, eg. show OSD"
# qdbus6 org.kde.ScreenBrightness /org/kde/ScreenBrightness AdjustBrightnessStep 1 0

# "get display names" + "get its brightness level"
# qdbus6 org.kde.ScreenBrightness /org/kde/ScreenBrightness DisplaysDBusNames \
# | xargs -I{} qdbus6 org.kde.ScreenBrightness /org/kde/ScreenBrightness/{} Brightness

# qdbus6 org.kde.ScreenBrightness /org/kde/ScreenBrightness/display0 org.kde.ScreenBrightness.Display.SetBrightness 80000 1

# qdbus6 org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl brightness
# qdbus6 org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl org.kde.Solid.PowerManagement.Actions.BrightnessControl.brightness

# qdbus6 org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl org.kde.Solid.PowerManagement.Actions.BrightnessControl.setBrightness 8000
# qdbus6 org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl org.kde.Solid.PowerManagement.Actions.BrightnessControl.setBrightnessSilent 8000

# qdbus6 org.kde.KWin.NightLight /org/kde/KWin/NightLight daylight

# xdotool key Shift+XF86MonBrightnessUp
# xdotool key XF86MonBrightnessUp
# xdotool key XF86MonBrightnessDown

# plasma-interactiveconsole --kwin
