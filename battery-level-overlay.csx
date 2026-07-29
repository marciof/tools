#!/usr/bin/dotnet run

/*
https://devblogs.microsoft.com/dotnet/announcing-dotnet-run-app/
https://dotnet.microsoft.com/en-us/download/dotnet/10.0
https://learn.microsoft.com/en-us/dotnet/core/sdk/file-based-apps

> winget install Microsoft.DotNet.SDK.10
> dotnet run battery-level-overlay.csx

OR to compile:

> dotnet publish battery-level-overlay.csx -o .

Requirements:

- Single file to run as-is like a script (eg. maybe .csx). No compilation step, so maybe using `dotnet run`, or `CSI.EXE`, or `Roslyn`, or `CS-Script`, or similar. No helper companion files (eg. .bat .cmd .vbs) to run it should be needed.
- Zero to minimal external dependencies, other than what's built-in and provided on a stock Windows installation. Ok to require installs like `Install-Module`, but not ok to require installs like a full blown Visual Studio for development. Any dependencies must be official from Microsoft, or highly visible maintained open-source.
- Target is Windows 10 version 1703 (OS build 15063) for a performance-constrained Lenovo Yoga Book YB1-X91F/L. So maybe .NET Framework 4.8, C# 7.3, which means language features like "$" string interpolation aren't available.
- Forward compatible with Windows 11.
*/

#:property RuntimeIdentifier=win-x64
#:property Configuration=Release
#:property DebugType=none

#:property TargetFramework=net10.0-windows

#:property UseWindowsForms=true
#:property UseWPF=true

// FIXME or these?
/*#:property TargetFramework=net8.0-windows
#:property TargetFramework=net9.0-windows*/

#:property PublishSingleFile=true
#:property PublishTrimmed=false
#:property PublishReadyToRun=true
#:property PublishAot=false
#:property SelfContained=false

#:property OutputType=WinExe

using System;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Effects;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using System.Windows.Forms;
using System.Windows.Interop;
using System.Threading;


const int DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE = -3;
const string AppName = "Battery Level Overlay";
const bool ShowInTaskbar = false;

const string TextFont = "Arial";
const double TextFontSize = 20;
const string TextColor = "White";
const string TextOutlineColor = "Black";

const double TextPaddingLeft = 10;
const double TextPaddingTop = 10;
const double TextPaddingRight = 10;
const double TextPaddingBottom = 10;

const double TextMarginLeft = -7;
const double TextMarginRight = -7;
const double TextMarginBottom = -10;

bool isRightAligned = true;
const int UpdateBatteryLevelFreqSecs = 60;
const string UnknownBatteryLevelPlaceholder = "--";

try {
    WinApi.SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE);
}
catch (Exception ex) {
    Console.WriteLine("DPI Awareness initialization skipped or unsupported: " + ex.Message);
}

Thread staThread = new Thread(() => {

// https://learn.microsoft.com/dotnet/api/system.windows.threading.dispatchertimer
DispatcherTimer updateBatteryLevelTimer = new DispatcherTimer();
updateBatteryLevelTimer.Interval = TimeSpan.FromSeconds(UpdateBatteryLevelFreqSecs);

// https://learn.microsoft.com/dotnet/api/system.windows.media.effects.dropshadoweffect
DropShadowEffect textOutline = new DropShadowEffect();
textOutline.Color = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(TextOutlineColor);
textOutline.ShadowDepth = 0;
textOutline.BlurRadius = 10;
textOutline.Opacity = 1;

// https://devblogs.microsoft.com/oldnewthing/20251020-00/?p=111706
IntPtr yellowUmbrellaIconHandle = WinApi.ExtractIcon(IntPtr.Zero, "pifmgr.dll", 1);
System.Drawing.Icon? trayIconImage = null;
if (yellowUmbrellaIconHandle != IntPtr.Zero) {
    trayIconImage = System.Drawing.Icon.FromHandle(yellowUmbrellaIconHandle);
}

// https://learn.microsoft.com/dotnet/api/system.windows.forms.notifyicon
NotifyIcon trayIcon = new NotifyIcon();
if (trayIconImage != null) trayIcon.Icon = trayIconImage;
trayIcon.Text = AppName;
trayIcon.Visible = true;

System.Windows.Controls.MenuItem exitMenuItem = new System.Windows.Controls.MenuItem();
exitMenuItem.Header = "Exit";

System.Windows.Controls.ContextMenu trayIconMenu = new System.Windows.Controls.ContextMenu();
trayIconMenu.Items.Add(exitMenuItem);

// https://learn.microsoft.com/dotnet/api/system.windows.controls.textblock
TextBlock textBlock = new TextBlock();
textBlock.ContextMenu = trayIconMenu;
textBlock.Effect = textOutline;
textBlock.Text = UnknownBatteryLevelPlaceholder + "%";
textBlock.Foreground = (System.Windows.Media.Brush)new System.Windows.Media.BrushConverter().ConvertFromString(TextColor);
textBlock.TextAlignment = TextAlignment.Right;
textBlock.VerticalAlignment = VerticalAlignment.Bottom;
textBlock.HorizontalAlignment = System.Windows.HorizontalAlignment.Right;
textBlock.Margin = new Thickness(TextPaddingLeft, TextPaddingTop, TextPaddingRight, TextPaddingBottom);
textBlock.FontFamily = new System.Windows.Media.FontFamily(TextFont);
textBlock.FontSize = TextFontSize;

// https://learn.microsoft.com/dotnet/api/system.windows.window
Window window = new Window();
window.Title = AppName;
window.Topmost = true;
window.ShowInTaskbar = ShowInTaskbar;
window.ShowActivated = false;
window.Focusable = false;
window.WindowStyle = WindowStyle.None;
window.SizeToContent = SizeToContent.WidthAndHeight;
window.AllowsTransparency = true;
window.Background = System.Windows.Media.Brushes.Transparent;
window.ResizeMode = ResizeMode.NoResize;
window.WindowStartupLocation = WindowStartupLocation.Manual;
window.Content = textBlock;

if (yellowUmbrellaIconHandle != IntPtr.Zero) {
    window.Icon = Imaging.CreateBitmapSourceFromHIcon(
        yellowUmbrellaIconHandle,
        Int32Rect.Empty,
        BitmapSizeOptions.FromEmptyOptions());
}

Action updateBatteryLevel = () => {
    try {
        // https://learn.microsoft.com/dotnet/api/system.windows.forms.systeminformation.powerstatus
        var power = System.Windows.Forms.SystemInformation.PowerStatus;
        bool isUnknown = power.BatteryChargeStatus == System.Windows.Forms.BatteryChargeStatus.Unknown ||
                         power.BatteryChargeStatus == System.Windows.Forms.BatteryChargeStatus.NoSystemBattery;

        textBlock.Text = isUnknown
            ? UnknownBatteryLevelPlaceholder + "%"
            : Math.Round(power.BatteryLifePercent * 100).ToString() + "%";
    }
    catch (Exception ex) {
        Console.WriteLine("Error reading battery metrics: " + ex.Message);
    }
};

Action updateWindowPosition = () => {
    // https://learn.microsoft.com/dotnet/api/system.windows.uielement.updatelayout
    window.UpdateLayout();

    // https://learn.microsoft.com/dotnet/api/system.windows.systemparameters.workarea
    var workArea = SystemParameters.WorkArea;
    window.Top = workArea.Bottom - window.ActualHeight - TextMarginBottom;

    window.Left = isRightAligned
        ? workArea.Right - window.ActualWidth - TextMarginRight
        : window.Left = workArea.Left + TextMarginLeft;
};

window.MouseDown += (sender, e) => {
    if (e.ChangedButton == System.Windows.Input.MouseButton.Left) {
        isRightAligned = !isRightAligned;
        updateWindowPosition();
    }
    else if (e.ChangedButton == System.Windows.Input.MouseButton.Right) {
        IntPtr handle = new WindowInteropHelper(window).Handle;
        WinApi.SetForegroundWindow(handle);
    }
};

trayIcon.MouseUp += (sender, e) => {
    if (e.Button == System.Windows.Forms.MouseButtons.Right) {
        IntPtr handle = new WindowInteropHelper(window).Handle;
        WinApi.SetForegroundWindow(handle);
        trayIconMenu.IsOpen = true;
    }
};

exitMenuItem.Click += (sender, e) => window.Close();
window.ContentRendered += (sender, e) => { updateBatteryLevel(); updateWindowPosition(); };
window.SizeChanged += (sender, e) => updateWindowPosition();
window.DpiChanged += (sender, e) => updateWindowPosition();

window.Closed += (sender, e) => {
    updateBatteryLevelTimer.Stop();
    trayIcon.Visible = false;
    trayIcon.Dispose();
    if (yellowUmbrellaIconHandle != IntPtr.Zero)
    {
        WinApi.DestroyIcon(yellowUmbrellaIconHandle);
    }
};

window.SourceInitialized += (sender, e) => {
    IntPtr handle = new WindowInteropHelper(window).Handle;
    const int GWL_EXSTYLE = -20;
    IntPtr extStyle = WinApi.GetWindowLongPtr(handle, GWL_EXSTYLE);

    const long WS_EX_TOOLWINDOW = 0x00000080L;
    const long WS_EX_NOACTIVATE = 0x08000000L;

    long newStyle = extStyle.ToInt64() | WS_EX_NOACTIVATE;
    if (!ShowInTaskbar) {
        newStyle |= WS_EX_TOOLWINDOW;
    }

    WinApi.SetWindowLongPtr(handle, GWL_EXSTYLE, new IntPtr(newStyle));
};

// https://learn.microsoft.com/dotnet/api/system.console.cancelkeypress
Console.CancelKeyPress += (sender, e) => {
    e.Cancel = true; 
    window.Dispatcher.BeginInvoke(new Action(() => window.Close()));
};

bool isNewInstance;
using (Mutex singleInstanceMutex = new Mutex(true, "Global\\com.marciof.tools.batteryLevelOverlay", out isNewInstance))
{
    if (!isNewInstance) {
        System.Windows.Forms.MessageBox.Show(
            "Already running.",
            AppName,
            MessageBoxButtons.OK,
            MessageBoxIcon.Warning);
        return;
    }

    try {
        Console.WriteLine("Press Ctrl+C to stop.");
        updateBatteryLevelTimer.Tick += (sender, e) => updateBatteryLevel();
        updateBatteryLevelTimer.Start();
        window.ShowDialog();
    }
    catch (Exception ex) {
        System.Windows.Forms.MessageBox.Show(
            "Error: " + ex.Message,
            AppName,
            MessageBoxButtons.OK,
            MessageBoxIcon.Error);
    }
    finally {
        try { singleInstanceMutex.ReleaseMutex(); } catch { }
    }
}
});


staThread.SetApartmentState(ApartmentState.STA);
staThread.Start();
staThread.Join();

// https://learn.microsoft.com/dotnet/standard/native-interop/pinvoke
public static class WinApi {

    [DllImport("user32.dll", EntryPoint = "GetWindowLong", SetLastError = true)]
    private static extern IntPtr GetWindowLong32(IntPtr hWnd, int nIndex);

    [DllImport("user32.dll", EntryPoint = "GetWindowLongPtr", SetLastError = true)]
    private static extern IntPtr GetWindowLongPtr64(IntPtr hWnd, int nIndex);

    // Architecture-safe wrapper for 32-bit and 64-bit compatibility
    public static IntPtr GetWindowLongPtr(IntPtr hWnd, int nIndex) {
        return IntPtr.Size == 8 ? GetWindowLongPtr64(hWnd, nIndex) : GetWindowLong32(hWnd, nIndex);
    }

    [DllImport("user32.dll", EntryPoint = "SetWindowLong", SetLastError = true)]
    private static extern IntPtr SetWindowLong32(IntPtr hWnd, int nIndex, IntPtr dwNewLong);

    [DllImport("user32.dll", EntryPoint = "SetWindowLongPtr", SetLastError = true)]
    private static extern IntPtr SetWindowLongPtr64(IntPtr hWnd, int nIndex, IntPtr dwNewLong);

    public static IntPtr SetWindowLongPtr(IntPtr hWnd, int nIndex, IntPtr dwNewLong) {
        return IntPtr.Size == 8 ? SetWindowLongPtr64(hWnd, nIndex, dwNewLong) : SetWindowLong32(hWnd, nIndex, dwNewLong);
    }

    // https://learn.microsoft.com/windows/win32/api/shellapi/nf-shellapi-extracticonw
    [DllImport("shell32.dll", CharSet = CharSet.Auto)]
    public static extern IntPtr ExtractIcon(IntPtr hInst, string lpszExeFileName, int nIconIndex);

    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool DestroyIcon(IntPtr hIcon);

    // https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setprocessdpiawarenesscontext
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetProcessDpiAwarenessContext(int dpiContext);

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
}
