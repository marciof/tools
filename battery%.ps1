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
    [DllImport("user32.dll")] public static extern int GetWindowLong(IntPtr hWnd, int nIndex);
    [DllImport("user32.dll")] public static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);
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


$batteryLevelTimer = New-Object System.Windows.Threading.DispatcherTimer
$batteryLevelTimer.Interval = [TimeSpan]::FromSeconds($updateBatteryLevelFreqSecs)

$textOutline = New-Object System.Windows.Media.Effects.DropShadowEffect
$textOutline.Color = [System.Windows.Media.Colors]::$textOutlineColor
$textOutline.ShadowDepth = 0
$textOutline.BlurRadius = 10
$textOutline.Opacity = 1

$textBlock = New-Object System.Windows.Controls.TextBlock
$textBlock.Effect = $textOutline
$textBlock.Text = "${unknownBatteryLevelPlaceholder}%"
$textBlock.Foreground = [System.Windows.Media.Brushes]::$textColor
$textBlock.FontSize = $textFontSize
$textBlock.FontFamily = New-Object System.Windows.Media.FontFamily($textFont)
$textBlock.TextAlignment = 'Right'
$textBlock.VerticalAlignment = 'Bottom'
$textBlock.HorizontalAlignment = 'Right'
$textBlock.Margin = "${textPaddingLeft},${textPaddingTop},${textPaddingRight},${textPaddingBottom}"

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

$exitMenuItem = New-Object System.Windows.Forms.ToolStripMenuItem('Exit')
$exitMenuItem.Add_Click({ $window.Close() })

$trayIconMenu = New-Object System.Windows.Forms.ContextMenuStrip
$trayIconMenu.Items.Add($exitMenuItem) | Out-Null

$trayIcon = New-Object System.Windows.Forms.NotifyIcon
$trayIcon.Icon = [System.Drawing.SystemIcons]::Application
$trayIcon.Text = $appName
$trayIcon.Visible = $true
$trayIcon.ContextMenuStrip = $trayIconMenu


$updateBatteryLevel = {
    Write-Host 'Updating battery level...'
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
    $window.UpdateLayout()
    $WorkArea = [System.Windows.SystemParameters]::WorkArea
    $window.Left = $WorkArea.Right - $window.ActualWidth
    $window.Top = $WorkArea.Bottom - $window.ActualHeight
}

$window.Add_ContentRendered({
    & $updateBatteryLevel
    & $UpdateWindowPosition
})

$window.Add_SizeChanged({
    & $UpdateWindowPosition
})

$window.Add_Closed({
    $batteryLevelTimer.Stop()
	$trayIcon.Visible = $false
	$trayIcon.Dispose()
})

$window.Add_SourceInitialized({
    $hwnd = (New-Object System.Windows.Interop.WindowInteropHelper($window)).Handle
    $exStyle = [Win32.NativeMethods]::GetWindowLong($hwnd, -20) # GWL_EXSTYLE
    
    # WS_EX_TOOLWINDOW (0x80)
    # WS_EX_NOACTIVATE (0x08000000)
    # WS_EX_TRANSPARENT (0x20) aka window click-through
    $exStyle = $exStyle -bor 0x80 -bor 0x08000000 -bor 0x20
    
    [void][Win32.NativeMethods]::SetWindowLong($hwnd, -20, $exStyle)
})

[System.Console]::add_CancelKeyPress({
    $EventArgs.Cancel = $true
    $window.Dispatcher.Invoke([System.Action]{ $window.Close() })
})


Write-Host 'Press Ctrl+C to stop.'
$batteryLevelTimer.Add_Tick($updateBatteryLevel)
$batteryLevelTimer.Start()
$window.ShowDialog() | Out-Null
