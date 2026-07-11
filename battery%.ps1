# https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_requires
#Requires -Version 5.1 # Windows 10

# https://learn.microsoft.com/powershell/module/microsoft.powershell.core/set-strictmode
Set-StrictMode -Version 3


# https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/add-type
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# https://learn.microsoft.com/dotnet/standard/native-interop/pinvoke
Add-Type -Namespace Win32 -Name NativeMethods -MemberDefinition @'
    [DllImport("user32.dll")]
    public static extern IntPtr GetWindowLongPtr(IntPtr hWnd, int nIndex);

    [DllImport("user32.dll")]
    public static extern IntPtr SetWindowLongPtr(
        IntPtr hWnd, int nIndex, IntPtr dwNewLong);

    [DllImport("shell32.dll")]
    public static extern IntPtr ExtractIcon(
        IntPtr hInst, string lpszExeFileName, int nIconIndex);
'@


$appName = 'Battery Level'

$textFont = 'Arial'
$textFontSize = 20
$textColor = 'White'
$textOutlineColor = 'Black'

$textPaddingLeft = 10
$textPaddingTop = 10
$textPaddingRight = 10
$textPaddingBottom = 10

$updateBatteryLevelFreqSecs = 30
$unknownBatteryLevelPlaceholder = '--'

# https://learn.microsoft.com/dotnet/api/system.windows.threading.dispatchertimer
$batteryLevelTimer = New-Object System.Windows.Threading.DispatcherTimer
$batteryLevelTimer.Interval = [TimeSpan]::FromSeconds($updateBatteryLevelFreqSecs)

# https://learn.microsoft.com/dotnet/api/system.windows.media.effects.dropshadoweffect
$textOutline = New-Object System.Windows.Media.Effects.DropShadowEffect
$textOutline.Color = [System.Windows.Media.Colors]::$textOutlineColor
$textOutline.ShadowDepth = 0
$textOutline.BlurRadius = 10
$textOutline.Opacity = 1

# https://learn.microsoft.com/dotnet/api/system.windows.controls.textblock
$textBlock = New-Object System.Windows.Controls.TextBlock
$textBlock.Effect = $textOutline
$textBlock.Text = "${unknownBatteryLevelPlaceholder}%"
$textBlock.Foreground = [System.Windows.Media.Brushes]::$textColor
$textBlock.TextAlignment = 'Right'
$textBlock.VerticalAlignment = 'Bottom'
$textBlock.HorizontalAlignment = 'Right'
$textBlock.Margin = "${textPaddingLeft},${textPaddingTop},${textPaddingRight},${textPaddingBottom}"

# https://learn.microsoft.com/dotnet/api/system.windows.media.fontfamily
$textBlock.FontFamily = New-Object System.Windows.Media.FontFamily($textFont)
$textBlock.FontSize = $textFontSize

# https://learn.microsoft.com/dotnet/api/system.windows.window
$window = New-Object System.Windows.Window
$window.Title = $appName
$window.Topmost = $true
$window.ShowInTaskbar = $false
$window.ShowActivated = $false
$window.Focusable = $false
$window.WindowStyle = 'None'
$window.SizeToContent = 'WidthAndHeight'
$window.AllowsTransparency = $true
$window.Background = [System.Windows.Media.Brushes]::Transparent
$window.ResizeMode = 'NoResize' # Windows 10 Tablet Mode
$window.WindowStartupLocation = 'Manual'
$window.Content = $textBlock

# https://learn.microsoft.com/dotnet/api/system.windows.forms.toolstripmenuitem
$exitMenuItem = New-Object System.Windows.Forms.ToolStripMenuItem('Exit')
$exitMenuItem.Add_Click({ $window.Close() })

# https://learn.microsoft.com/dotnet/api/system.windows.forms.contextmenustrip
$trayIconMenu = New-Object System.Windows.Forms.ContextMenuStrip
$trayIconMenu.Items.Add($exitMenuItem) | Out-Null

# https://learn.microsoft.com/dotnet/api/system.windows.forms.notifyicon
$trayIcon = New-Object System.Windows.Forms.NotifyIcon
$trayIcon.Icon = [System.Drawing.Icon]::FromHandle(
    [Win32.NativeMethods]::ExtractIcon(
        [IntPtr]::Zero, "pifmgr.dll", 1)) # yellow umbrella
$trayIcon.Text = $appName
$trayIcon.Visible = $true
$trayIcon.ContextMenuStrip = $trayIconMenu


$updateBatteryLevel = {
    Write-Host 'Updating battery level...'

    # https://learn.microsoft.com/powershell/module/cimcmdlets/get-ciminstance
    # https://learn.microsoft.com/windows/win32/cimwin32prov/win32-battery
    $batteries = Get-CimInstance -ClassName Win32_Battery -ErrorAction SilentlyContinue

    if (-not $batteries) {
        $textBlock.Text = "${unknownBatteryLevelPlaceholder}%"
    }
    else {
        $stats = $batteries | Measure-Object -Property EstimatedChargeRemaining -Average
        $level = [Math]::Round($stats.Average)
        $textBlock.Text = "${level}%"
    }
}

$UpdateWindowPosition = {
    # https://learn.microsoft.com/dotnet/api/system.windows.uielement.updatelayout
    $window.UpdateLayout()

    # https://learn.microsoft.com/dotnet/api/system.windows.systemparameters.workarea
    $WorkArea = [System.Windows.SystemParameters]::WorkArea
    $window.Left = $WorkArea.Right - $window.ActualWidth
    $window.Top = $WorkArea.Bottom - $window.ActualHeight
}

# https://learn.microsoft.com/dotnet/api/system.windows.window.contentrendered
$window.Add_ContentRendered({
    & $updateBatteryLevel
    & $UpdateWindowPosition
})

# https://learn.microsoft.com/dotnet/api/system.windows.frameworkelement.sizechanged
$window.Add_SizeChanged({
    & $UpdateWindowPosition
})

# https://learn.microsoft.com/dotnet/api/system.windows.window.closed
$window.Add_Closed({
    $batteryLevelTimer.Stop()
	$trayIcon.Visible = $false
	$trayIcon.Dispose()
})

# https://learn.microsoft.com/dotnet/api/system.windows.window.sourceinitialized
$window.Add_SourceInitialized({
    # https://learn.microsoft.com/dotnet/api/system.windows.interop.windowinterophelper
    $windowHandle = (New-Object System.Windows.Interop.WindowInteropHelper($window)).Handle

    # https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getwindowlongptrw
    $GWL_EXSTYLE = -20
    $windowExtStyle = [Win32.NativeMethods]::GetWindowLongPtr($windowHandle, $GWL_EXSTYLE)

    # https://learn.microsoft.com/windows/win32/winmsg/extended-window-styles
    $WS_EX_TOOLWINDOW = 0x80
    $WS_EX_NOACTIVATE = 0x8000000
    $WS_EX_TRANSPARENT = 0x20 # pass-through mouse clicks
    $windowExtStyle = [IntPtr]($windowExtStyle -bor $WS_EX_TOOLWINDOW -bor $WS_EX_NOACTIVATE -bor $WS_EX_TRANSPARENT)

    # https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setwindowlongptrw
    [void][Win32.NativeMethods]::SetWindowLongPtr($windowHandle, $GWL_EXSTYLE, $windowExtStyle)
})

# https://learn.microsoft.com/dotnet/api/system.console.cancelkeypress
[System.Console]::add_CancelKeyPress({
    $window.Dispatcher.Invoke([System.Action]{ $window.Close() })
})


Write-Host 'Press Ctrl+C to stop.'
$batteryLevelTimer.Add_Tick($updateBatteryLevel)
$batteryLevelTimer.Start()
$window.ShowDialog() | Out-Null
