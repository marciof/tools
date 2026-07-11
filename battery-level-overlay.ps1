# https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_requires
# https://learn.microsoft.com/powershell/scripting/dev-cross-plat/performance/script-authoring-considerations
#Requires -Version 5.1 # Windows 10

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
'@


$appName = 'Battery Level Overlay'

$textFont = 'Arial'
$textFontSize = 20
$textColor = 'White'
$textOutlineColor = 'Black'

# Reducing padding too much will crop outline effects.
$textPaddingLeft = 10
$textPaddingTop = 10
$textPaddingRight = 10
$textPaddingBottom = 10

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

# https://learn.microsoft.com/dotnet/api/system.windows.controls.textblock
$textBlock = [System.Windows.Controls.TextBlock]::new()
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
$exitMenuItem = [System.Windows.Forms.ToolStripMenuItem]::new('Exit')
$exitMenuItem.Add_Click({ $window.Close() })

# https://learn.microsoft.com/dotnet/api/system.windows.forms.contextmenustrip
$trayIconMenu = [System.Windows.Forms.ContextMenuStrip]::new()
$null = $trayIconMenu.Items.Add($exitMenuItem)

# https://devblogs.microsoft.com/oldnewthing/20251020-00/?p=111706
# https://learn.microsoft.com/windows/win32/api/shellapi/nf-shellapi-extracticonw
$yellowUmbrellaIcon = [WinApi.Call]::ExtractIcon(
    [IntPtr]::Zero, "pifmgr.dll", 1)

# https://learn.microsoft.com/dotnet/api/system.windows.forms.notifyicon
$trayIcon = [System.Windows.Forms.NotifyIcon]::new()
$trayIcon.Icon = [System.Drawing.Icon]::FromHandle($yellowUmbrellaIcon)
$trayIcon.Text = $appName
$trayIcon.Visible = $true
$trayIcon.ContextMenuStrip = $trayIconMenu


$updateBatteryLevel = {
    # https://learn.microsoft.com/windows/win32/cimwin32prov/win32-battery
    # https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_wql
    # https://learn.microsoft.com/dotnet/api/system.management.managementobjectsearcher
    $searcher = [System.Management.ManagementObjectSearcher]::new(
        'SELECT EstimatedChargeRemaining FROM Win32_Battery')

    $batteries = $searcher.Get()
    $levelSum = 0
    $numBatteries = 0

    foreach ($battery in $batteries) {
        $levelSum += [int] $battery['EstimatedChargeRemaining']
        $numBatteries++
    }

    $textBlock.Text = if ($numBatteries -eq 0) {
        "${unknownBatteryLevelPlaceholder}%"
    } else {
        "$([Math]::Round($levelSum / $numBatteries))%"
    }
}

$UpdateWindowPosition = {
    # https://learn.microsoft.com/dotnet/api/system.windows.uielement.updatelayout
    $window.UpdateLayout()

    # https://learn.microsoft.com/dotnet/api/system.windows.systemparameters.workarea
    $WorkArea = [System.Windows.SystemParameters]::WorkArea
    $window.Top = $WorkArea.Bottom - $window.ActualHeight - $textMarginBottom

    $window.Left = if ($isRightAligned) {
        $WorkArea.Right - $window.ActualWidth - $textMarginRight
    }
    else {
        $WorkArea.Left
    }
}

# https://learn.microsoft.com/dotnet/api/system.windows.uielement.mousedown
$window.Add_MouseDown({
    param(
        [object] $sender,
        [System.Windows.Input.MouseButtonEventArgs] $event
    )

    if ($event.RightButton -eq 'Pressed') {
        $trayIconMenu.Show([System.Windows.Forms.Cursor]::Position)
    }
    else {
        # TODO maybe nice to switch font/outline colors too?
        $script:isRightAligned = -not $script:isRightAligned
        & $UpdateWindowPosition
    }
})

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
    $extStyle = [IntPtr] (
        $extStyle -bor $WS_EX_TOOLWINDOW -bor $WS_EX_NOACTIVATE)

    # https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setwindowlongptrw
    $null = [WinApi.Call]::SetWindowLongPtr($handle, $GWL_EXSTYLE, $extStyle)
})

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
    Write-Host 'Press Ctrl+C to stop.'
    $updateBatteryLevelTimer.Add_Tick($updateBatteryLevel)
    $updateBatteryLevelTimer.Start()
    $null = $window.ShowDialog()
}
finally {
    $singleInstanceMutex.ReleaseMutex()
    $singleInstanceMutex.Dispose()
}
