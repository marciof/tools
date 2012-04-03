import XMonad
import XMonad.Config.Kde
import XMonad.Layout.NoFrillsDecoration
import XMonad.Layout.SimpleDecoration
import XMonad.Util.EZConfig
import XMonad.StackSet

-- http://www.haskell.org/haskellwiki/Xmonad/Using_xmonad_in_KDE

main = xmonad $ kde4Config {
    -- Windows key as modifier?
    -- modMask = mod4Mask,
    layoutHook = noFrillsDeco shrinkText defaultTheme (layoutHook kde4Config),
    focusedBorderColor = "#007BFF"
} `additionalKeysP` [
        ("M-<Up>", windows focusUp),
        ("M-<Down>", windows focusDown),
        ("M-<Left>", sendMessage Shrink),
        ("M-<Right>", sendMessage Expand)
    ]
