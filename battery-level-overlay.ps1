# Setup:
#   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# Dependencies (test): PSScriptAnalyzer
#   Invoke-ScriptAnalyzer -Settings @{Rules=@{PSUseCompatibleSyntax=@{Enable=$true;TargetVersions='5.1'}}} -Severity Error,Warning,Information

# TODO error handling
# TODO tests
# TODO document (+ dependencies + setup)
# TODO logging

# TODO slow startup, use C++? this uses C#, and C#'s still verbose w/ hardcoding
# TODO does the percentage level go to 0% after resuming hibernation?

# TODO add option to not always show a percentage? eg:
#   - low/critical/reserve user settings from system control panel?
#   - https://learn.microsoft.com/dotnet/api/system.windows.forms.batterychargestatus
#   - alt text? ok, low, critical, reserve
#   - symbols?  ".........."
#   - rounding? up ≥15% -> ~20%, down <15% -> ~10%, then 9% 8% ... 1%
#   - prefixes? ~60% +60% >60% ≥60% ⚡60%

# Target Windows 10 / Lenovo Yoga Book YB1-X91.
# https://learn.microsoft.com/powershell/scripting/install/powershell-support-lifecycle#windows-powershell-release-history
#Requires -Version 5.1

# Avoid `Add-Type -AssemblyName` for performance.
# https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_using#assembly-syntax
using assembly PresentationFramework
using assembly PresentationCore
using assembly WindowsBase
using assembly System.Windows.Forms
using assembly System.Drawing

Set-StrictMode -Version 3

[string] $appName = 'Battery Level Overlay'
[string] $namespace = 'com.marciof.tools.batteryLevelOverlay'

$isNewInstance = $false
$singleInstanceMutex = [System.Threading.Mutex]::new(
    $true, "Global\$namespace", [ref] $isNewInstance)

if (-not $isNewInstance) {
    $null = [System.Windows.Forms.MessageBox]::Show(
        'Already running.',
        $appName,
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Warning)
    Exit
}

# Ensure single-instance mutex is released...
try {
# ...at the end.

# Avoid inline C# compilation via `Add-Type -MemberDefinition` for performance.
$assemblyName = [System.Reflection.AssemblyName]::new($namespace)
$assemblyBuilder = [AppDomain]::CurrentDomain.DefineDynamicAssembly(
    $assemblyName, [System.Reflection.Emit.AssemblyBuilderAccess]::Run)

$moduleBuilder = $assemblyBuilder.DefineDynamicModule('WinApi')
$typeBuilder = $moduleBuilder.DefineType('WinApi.Call',
    [System.Reflection.TypeAttributes]::Public `
    -bor [System.Reflection.TypeAttributes]::Class)

$winApiCall = [System.Runtime.InteropServices.CallingConvention]::Winapi
$winApiCallCharset = [System.Runtime.InteropServices.CharSet]::Unicode

$winApiMethodCallConv = [System.Reflection.CallingConventions]::Standard
$winApiMethodAttrs = [System.Reflection.MethodAttributes]::Public `
    -bor [System.Reflection.MethodAttributes]::Static `
    -bor [System.Reflection.MethodAttributes]::PinvokeImpl

$typeBuilder.DefinePInvokeMethod('GetWindowLongPtr', 'user32.dll',
    $winApiMethodAttrs, $winApiMethodCallConv,
    [IntPtr], [Type[]]@([IntPtr], [int]),
    $winApiCall, $winApiCallCharset
).SetImplementationFlags('PreserveSig')

$typeBuilder.DefinePInvokeMethod('SetWindowLongPtr', 'user32.dll',
    $winApiMethodAttrs, $winApiMethodCallConv,
    [IntPtr], [Type[]]@([IntPtr], [int], [IntPtr]),
    $winApiCall, $winApiCallCharset
).SetImplementationFlags('PreserveSig')

$typeBuilder.DefinePInvokeMethod('ExtractIcon', 'shell32.dll',
    $winApiMethodAttrs, $winApiMethodCallConv,
    [IntPtr], [Type[]]@([IntPtr], [string], [int]),
    $winApiCall, $winApiCallCharset
).SetImplementationFlags('PreserveSig')

$typeBuilder.DefinePInvokeMethod('DestroyIcon', 'user32.dll',
    $winApiMethodAttrs, $winApiMethodCallConv,
    [bool], [Type[]]@([IntPtr]),
    $winApiCall, $winApiCallCharset
).SetImplementationFlags('PreserveSig')

$typeBuilder.DefinePInvokeMethod('SetProcessDpiAwarenessContext', 'user32.dll',
    $winApiMethodAttrs, $winApiMethodCallConv,
    [bool], [Type[]]@([int]),
    $winApiCall, $winApiCallCharset
).SetImplementationFlags('PreserveSig')

$typeBuilder.DefinePInvokeMethod('SetForegroundWindow', 'user32.dll',
    $winApiMethodAttrs, $winApiMethodCallConv,
    [bool], [Type[]]@([IntPtr]),
    $winApiCall, $winApiCallCharset
).SetImplementationFlags('PreserveSig')

$null = $typeBuilder.CreateType()

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
$null = [WinApi.Call]::SetProcessDpiAwarenessContext($DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE)

[bool] $showInTaskbar = $false

[string] $textFont = 'Arial'
[int] $textFontSize = 20
[string] $textColor = 'White'
[string] $textOutlineColor = 'Black'

# Reducing padding too much will crop outline effects.
[int] $textPaddingLeft = 10
[int] $textPaddingTop = 10
[int] $textPaddingRight = 10
[int] $textPaddingBottom = 10

# Eyeballed.
[int] $textMarginLeft = -7
[int] $textMarginRight = -7
[int] $textMarginBottom = -10

[bool] $isRightAligned = $true
[int] $updateBatteryLevelFreqSecs = 60
[string] $unknownBatteryLevelPlaceholder = '--'

$updateBatteryLevelTimer = [System.Windows.Threading.DispatcherTimer]::new()
$updateBatteryLevelTimer.Interval = [TimeSpan]::FromSeconds(
    $updateBatteryLevelFreqSecs)

$textOutline = [System.Windows.Media.Effects.DropShadowEffect]::new()
$textOutline.Color = [System.Windows.Media.Colors]::$textOutlineColor
$textOutline.ShadowDepth = 0
$textOutline.BlurRadius = 10
$textOutline.Opacity = 1

# https://devblogs.microsoft.com/oldnewthing/20251020-00/?p=111706
$yellowUmbrellaIcon = [WinApi.Call]::ExtractIcon(
    [IntPtr]::Zero, "pifmgr.dll", 1)

$trayIcon = [System.Windows.Forms.NotifyIcon]::new()
$trayIcon.Icon = [System.Drawing.Icon]::FromHandle($yellowUmbrellaIcon)
$trayIcon.Text = $appName
$trayIcon.Visible = $true

$exitMenuItem = [System.Windows.Controls.MenuItem]::new()
$exitMenuItem.Header = 'Exit'

$trayIconMenu = [System.Windows.Controls.ContextMenu]::new()
$null = $trayIconMenu.Items.Add($exitMenuItem)

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

$textBlock.FontFamily = [System.Windows.Media.FontFamily]::new($textFont)
$textBlock.FontSize = $textFontSize

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
$window.ResizeMode = 'NoResize' # Windows 10 tablet mode.
$window.WindowStartupLocation = 'Manual'
$window.Content = $textBlock

$window.Icon = [System.Windows.Interop.Imaging]::CreateBitmapSourceFromHIcon(
    $yellowUmbrellaIcon,
    [System.Windows.Int32Rect]::Empty,
    [System.Windows.Media.Imaging.BitmapSizeOptions]::FromEmptyOptions())

$updateBatteryLevel = {
    $power = [System.Windows.Forms.SystemInformation]::PowerStatus

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
    $window.UpdateLayout()

    $workArea = [System.Windows.SystemParameters]::WorkArea
    $window.Top = $workArea.Bottom - $window.ActualHeight - $textMarginBottom

    $window.Left = if ($isRightAligned) {
        $workArea.Right - $window.ActualWidth - $textMarginRight
    }
    else {
        $workArea.Left + $textMarginLeft
    }
}

$window.Add_MouseDown({
    param(
        [System.Windows.Window] $eSender,
        [System.Windows.Input.MouseButtonEventArgs] $eArgs)

    if ($eArgs.ChangedButton -eq [System.Windows.Input.MouseButton]::Left) {
        $script:isRightAligned = -not $script:isRightAligned
        & $updateWindowPosition
    }
    elseif ($eArgs.ChangedButton -eq [System.Windows.Input.MouseButton]::Right) {
        $handle = ([System.Windows.Interop.WindowInteropHelper]::new($window)).Handle
        $null = [WinApi.Call]::SetForegroundWindow($handle)
    }
})

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

$exitMenuItem.Add_Click({ $window.Close() })
$window.Add_SizeChanged({ & $updateWindowPosition })
$window.Add_DpiChanged({ & $updateWindowPosition })

$window.Add_ContentRendered({
    & $updateBatteryLevel
    & $updateWindowPosition
})

$window.Add_Closed({
    $updateBatteryLevelTimer.Stop()
	$trayIcon.Visible = $false
	$trayIcon.Dispose()
    $null = [WinApi.Call]::DestroyIcon($yellowUmbrellaIcon)
})

$window.Add_SourceInitialized({
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

    $null = [WinApi.Call]::SetWindowLongPtr($handle, $GWL_EXSTYLE, $extStyle)
})

# TODO long delay between keypress and action
[System.Console]::add_CancelKeyPress({
    $window.Dispatcher.Invoke([System.Action]{ $window.Close() })
})

Write-Information 'Press Ctrl+C to stop.'
$updateBatteryLevelTimer.Add_Tick($updateBatteryLevel)
$updateBatteryLevelTimer.Start()
$null = $window.ShowDialog()

# (Mutex acquired at the start.)
} finally {
    $singleInstanceMutex.ReleaseMutex()
    $singleInstanceMutex.Dispose()
}
