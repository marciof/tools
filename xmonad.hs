import XMonad
import XMonad.Config.Kde
import XMonad.Layout.NoFrillsDecoration
import XMonad.Layout.SimpleDecoration
import XMonad.Util.EZConfig
import XMonad.StackSet
import XMonad.Actions.RotSlaves

-- http://www.haskell.org/haskellwiki/Xmonad/Using_xmonad_in_KDE

main = xmonad $ kde4Config {
    -- Windows key as modifier?
    -- modMask = mod4Mask,
    layoutHook = noFrillsDeco shrinkText defaultTheme (layoutHook kde4Config),
    focusedBorderColor = "#007BFF"
} `additionalKeysP` [
        -- ("M-<Left>", rotAllUp),
        -- ("M-<Right>", rotAllDown),
        ("M-<Up>", sendMessage Expand),
        ("M-<Down>", sendMessage Shrink),
        ("M-<Tab>", windows focusDown),
        ("M-S-<Tab>", windows focusUp)
    ]
