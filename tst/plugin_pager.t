Setup:

  $ . "$TESTDIR/setup.sh"

Disable pager on slow input:

  $ (echo begin && sleep 1 && echo end) | show
  begin
  end

Discard output:

  $ show > /dev/null
