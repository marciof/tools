#include <Windows.h>


int main() {
    BOOL didSucceed = SystemParametersInfo(
        SPI_SETCURSORSHADOW,
        0,
        (PVOID) TRUE,
        SPIF_UPDATEINIFILE + SPIF_SENDCHANGE);
    
    return didSucceed ? EXIT_SUCCESS : EXIT_FAILURE;
}


/*
--- Via INF file ---

[Version]
Signature=$CHICAGO$

[DefaultInstall]
AddReg=Reg.Settings
BitReg=Bit.Settings

[Reg.Settings]
HKLM,Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects\CursorShadow,DefaultValue,0x00010001,1

[Bit.Settings]
HKCU,"Control Panel\Desktop",UserPreferencesMask,1,0x20,1
*/
