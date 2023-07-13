import amoshell

mo = amoshell.Amos()
rval, out, err = mo.moshell('WTC1EENB84', 'lt all; alt')
if rval:
    print(err)
else:
    print(out)