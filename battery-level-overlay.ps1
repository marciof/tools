#!/usr/bin/env pwsh

# Dependencies (test): PSScriptAnalyzer
#   Invoke-ScriptAnalyzer -Settings @{Rules=@{PSUseCompatibleSyntax=@{Enable=$true;TargetVersions='5.1'}}} -Severity Error,Warning,Information

# https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_requires
# https://learn.microsoft.com/powershell/scripting/install/powershell-support-lifecycle#windows-powershell-release-history
# https://learn.microsoft.com/powershell/scripting/dev-cross-plat/performance/script-authoring-considerations
#Requires -Version 5.1 # Windows 10 / Lenovo Yoga Book YB1-X91

# TODO https://learn.microsoft.com/powershell/utility-modules/psscriptanalyzer/using-scriptanalyzer#check-powershell-version-compatibility
# https://learn.microsoft.com/powershell/module/microsoft.powershell.core/set-strictmode
Set-StrictMode -Version 3


# https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/add-type
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Management

# https://learn.microsoft.com/dotnet/standard/native-interop/pinvoke
# https://learn.microsoft.com/dotnet/api/system.runtime.interopservices.dllimportattribute.setlasterror
# https://learn.microsoft.com/dotnet/api/system.runtime.interopservices.unmanagedtype
Add-Type -Namespace WinApi -Name Call -MemberDefinition @'
    [DllImport("user32.dll")]
    public static extern IntPtr GetWindowLongPtr(IntPtr hWnd, int nIndex);

    [DllImport("user32.dll")]
    public static extern IntPtr SetWindowLongPtr(
        IntPtr hWnd, int nIndex, IntPtr dwNewLong);

    [DllImport("shell32.dll")]
    public static extern IntPtr ExtractIcon(
        IntPtr hInst, string lpszExeFileName, int nIconIndex);

    [DllImport("user32.dll", SetLastError=true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool DestroyIcon(IntPtr hIcon);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetProcessDpiAwarenessContext(int dpiContext);

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
'@


# v2 was introduced in Windows 10 version 1703 (OS build 15063):
# - https://learn.microsoft.com/windows/win32/hidpi/dpi-awareness-context
# - https://learn.microsoft.com/en-us/windows/uwp/whats-new/windows-10-build-15063
# Which was made available starting on 2017-04-11:
# - https://learn.microsoft.com/en-us/windows/release-health/release-information
# However Lenovo Yoga Book YB1-X91F/L was released in 2016:
# - https://blogs.windows.com/windowsexperience/2016/08/31/lenovo-announces-convertible-and-detachable-pcs-with-windows-10/
# - https://web.archive.org/web/20161019000522/http://news.lenovo.com/news-releases/lenovo-reveals-yoga-book-2-in-1-tablet-for-productivity-and-creativity.htm
# - https://pcsupport.lenovo.com/us/en/products/tablets/yoga-series/yoga-book/solutions/pd104400-overview-for-yoga-book
$DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE = -3

# https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setprocessdpiawarenesscontext
$null = [WinApi.Call]::SetProcessDpiAwarenessContext($DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE)


$appName = 'Battery Level Overlay'
$showInTaskbar = $false

$textFont = 'Arial'
$textFontSize = 20
$textColor = 'White'
$textOutlineColor = 'Black'

# Reducing padding too much will crop outline effects.
$textPaddingLeft = 10
$textPaddingTop = 10
$textPaddingRight = 10
$textPaddingBottom = 10

# Eyeballed.
$textMarginLeft = -7
$textMarginRight = -7
$textMarginBottom = -10

$isRightAligned = $true
$updateBatteryLevelFreqSecs = 60
$unknownBatteryLevelPlaceholder = '--'


# https://learn.microsoft.com/dotnet/api/system.windows.threading.dispatchertimer
$updateBatteryLevelTimer = [System.Windows.Threading.DispatcherTimer]::new()
$updateBatteryLevelTimer.Interval = [TimeSpan]::FromSeconds(
    $updateBatteryLevelFreqSecs)

# https://learn.microsoft.com/dotnet/api/system.windows.media.effects.dropshadoweffect
$textOutline = [System.Windows.Media.Effects.DropShadowEffect]::new()
$textOutline.Color = [System.Windows.Media.Colors]::$textOutlineColor
$textOutline.ShadowDepth = 0
$textOutline.BlurRadius = 10
$textOutline.Opacity = 1

# https://devblogs.microsoft.com/oldnewthing/20251020-00/?p=111706
# https://learn.microsoft.com/windows/win32/api/shellapi/nf-shellapi-extracticonw
$yellowUmbrellaIcon = [WinApi.Call]::ExtractIcon(
    [IntPtr]::Zero, "pifmgr.dll", 1)

# https://learn.microsoft.com/dotnet/api/system.windows.forms.notifyicon
$trayIcon = [System.Windows.Forms.NotifyIcon]::new()
$trayIcon.Icon = [System.Drawing.Icon]::FromHandle($yellowUmbrellaIcon)
$trayIcon.Text = $appName
$trayIcon.Visible = $true

# https://learn.microsoft.com/dotnet/api/system.windows.controls.menuitem
$exitMenuItem = [System.Windows.Controls.MenuItem]::new()
$exitMenuItem.Header = 'Exit'

# https://learn.microsoft.com/dotnet/api/system.windows.controls.contextmenu
$trayIconMenu = [System.Windows.Controls.ContextMenu]::new()
$null = $trayIconMenu.Items.Add($exitMenuItem)

# https://learn.microsoft.com/dotnet/api/system.windows.controls.textblock
$textBlock = [System.Windows.Controls.TextBlock]::new()
$textBlock.ContextMenu = $trayIconMenu
$textBlock.Effect = $textOutline
$textBlock.Text = "${unknownBatteryLevelPlaceholder}%"
$textBlock.Foreground = [System.Windows.Media.Brushes]::$textColor
$textBlock.TextAlignment = 'Right'
$textBlock.VerticalAlignment = 'Bottom'
$textBlock.HorizontalAlignment = 'Right'
$textBlock.Margin = [System.Windows.Thickness]::new(
    $textPaddingLeft, $textPaddingTop, $textPaddingRight, $textPaddingBottom)

# https://learn.microsoft.com/dotnet/api/system.windows.media.fontfamily
$textBlock.FontFamily = [System.Windows.Media.FontFamily]::new($textFont)
$textBlock.FontSize = $textFontSize

# https://learn.microsoft.com/dotnet/api/system.windows.window
$window = [System.Windows.Window]::new()
$window.Title = $appName
$window.Topmost = $true
$window.ShowInTaskbar = $showInTaskbar
$window.ShowActivated = $false
$window.Focusable = $false
$window.WindowStyle = 'None'
$window.SizeToContent = 'WidthAndHeight'
$window.AllowsTransparency = $true
$window.Background = [System.Windows.Media.Brushes]::Transparent
$window.ResizeMode = 'NoResize' # Windows 10 Tablet Mode
$window.WindowStartupLocation = 'Manual'
$window.Content = $textBlock

# https://learn.microsoft.com/dotnet/api/system.windows.interop.imaging.createbitmapsourcefromhicon
$window.Icon = [System.Windows.Interop.Imaging]::CreateBitmapSourceFromHIcon(
    $yellowUmbrellaIcon,
    [System.Windows.Int32Rect]::Empty,
    [System.Windows.Media.Imaging.BitmapSizeOptions]::FromEmptyOptions())


$updateBatteryLevel = {
    # https://learn.microsoft.com/dotnet/api/system.windows.forms.systeminformation.powerstatus
    $power = [System.Windows.Forms.SystemInformation]::PowerStatus

    # https://learn.microsoft.com/dotnet/api/system.windows.forms.batterychargestatus
    $isUnknown = $power.BatteryChargeStatus -in
        [System.Windows.Forms.BatteryChargeStatus]::Unknown,
        [System.Windows.Forms.BatteryChargeStatus]::NoSystemBattery

    $textBlock.Text = if ($isUnknown) {
        "${unknownBatteryLevelPlaceholder}%"
    }
    else {
        "$([Math]::Round($power.BatteryLifePercent * 100))%"
    }
}


$updateWindowPosition = {
    # https://learn.microsoft.com/dotnet/api/system.windows.uielement.updatelayout
    $window.UpdateLayout()

    # https://learn.microsoft.com/dotnet/api/system.windows.systemparameters.workarea
    $workArea = [System.Windows.SystemParameters]::WorkArea
    $window.Top = $workArea.Bottom - $window.ActualHeight - $textMarginBottom

    $window.Left = if ($isRightAligned) {
        $workArea.Right - $window.ActualWidth - $textMarginRight
    }
    else {
        $workArea.Left + $textMarginLeft
    }
}


# https://learn.microsoft.com/dotnet/api/system.windows.input.mousebuttoneventargs
# https://learn.microsoft.com/dotnet/api/system.windows.uielement.mouseup
$window.Add_MouseDown({
    param(
        [System.Windows.Window] $eSender,
        [System.Windows.Input.MouseButtonEventArgs] $eArgs)

    if ($eArgs.ChangedButton -eq [System.Windows.Input.MouseButton]::Left) {
        # TODO maybe nice to switch font/outline colors too?
        $script:isRightAligned = -not $script:isRightAligned
        & $updateWindowPosition
    }
    elseif ($eArgs.ChangedButton -eq [System.Windows.Input.MouseButton]::Right) {
        $handle = ([System.Windows.Interop.WindowInteropHelper]::new($window)).Handle
        $null = [WinApi.Call]::SetForegroundWindow($handle)
    }
})


# https://learn.microsoft.com/dotnet/api/system.windows.forms.mouseeventargs
# https://learn.microsoft.com/dotnet/api/system.windows.forms.notifyicon.mouseup
$trayIcon.Add_MouseUp({
    param(
        [System.Windows.Forms.NotifyIcon] $eSender,
        [System.Windows.Forms.MouseEventArgs] $eArgs)

    if ($eArgs.Button -eq [System.Windows.Forms.MouseButtons]::Right) {
        $handle = ([System.Windows.Interop.WindowInteropHelper]::new($window)).Handle
        $null = [WinApi.Call]::SetForegroundWindow($handle)
        $trayIconMenu.IsOpen = $true
    }
})


# https://learn.microsoft.com/dotnet/api/system.windows.controls.menuitem.onclick
$exitMenuItem.Add_Click({
    $window.Close()
})


# https://learn.microsoft.com/dotnet/api/system.windows.window.contentrendered
$window.Add_ContentRendered({
    & $updateBatteryLevel
    & $updateWindowPosition
})


# https://learn.microsoft.com/dotnet/api/system.windows.frameworkelement.sizechanged
$window.Add_SizeChanged({
    & $updateWindowPosition
})


# https://learn.microsoft.com/dotnet/api/system.windows.window.dpichanged
$window.Add_DpiChanged({
    & $updateWindowPosition
})


# https://learn.microsoft.com/dotnet/api/system.windows.window.closed
$window.Add_Closed({
    $updateBatteryLevelTimer.Stop()
	$trayIcon.Visible = $false
	$trayIcon.Dispose()
    $null = [WinApi.Call]::DestroyIcon($yellowUmbrellaIcon)
})


# https://learn.microsoft.com/dotnet/api/system.windows.window.sourceinitialized
$window.Add_SourceInitialized({
    # https://learn.microsoft.com/dotnet/api/system.windows.interop.windowinterophelper
    $handle = ([System.Windows.Interop.WindowInteropHelper]::new(
        $window)).Handle

    # https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getwindowlongptrw
    $GWL_EXSTYLE = -20
    $extStyle = [WinApi.Call]::GetWindowLongPtr($handle, $GWL_EXSTYLE)

    # https://learn.microsoft.com/windows/win32/winmsg/extended-window-styles
    $WS_EX_TOOLWINDOW = 0x80
    $WS_EX_NOACTIVATE = 0x8000000
    $extStyle = [IntPtr] ($extStyle `
        -bor $WS_EX_NOACTIVATE `
        -bor $(if ($showInTaskbar) { 0 } else { $WS_EX_TOOLWINDOW }))

    # https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setwindowlongptrw
    $null = [WinApi.Call]::SetWindowLongPtr($handle, $GWL_EXSTYLE, $extStyle)
})


# FIXME long delay between keypress and action (InvokeAsync didn't work)
# https://learn.microsoft.com/dotnet/api/system.console.cancelkeypress
[System.Console]::add_CancelKeyPress({
    $window.Dispatcher.Invoke([System.Action]{ $window.Close() })
})


$isNewInstance = $false

# https://learn.microsoft.com/dotnet/api/system.threading.mutex
$singleInstanceMutex = [System.Threading.Mutex]::new(
    $true, 'Global\com.marciof.tools.batteryLevelOverlay', [ref] $isNewInstance)

if (-not $isNewInstance) {
    $null = [System.Windows.Forms.MessageBox]::Show(
        'Already running.',
        $appName,
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Warning)
    Exit
}

try {
    Write-Information 'Press Ctrl+C to stop.'
    $updateBatteryLevelTimer.Add_Tick($updateBatteryLevel)
    $updateBatteryLevelTimer.Start()
    $null = $window.ShowDialog()
}
finally {
    $singleInstanceMutex.ReleaseMutex()
    $singleInstanceMutex.Dispose()
}
