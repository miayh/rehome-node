import amoshell
mo = amoshell.Amos()
rval, out, err = mo.moshell('WTC1EENB84', 'lt all')
if rval:
    print(err)
else:
    print(out)

results = mo.moshell('WTC1EENB84', 'get FieldReplaceableUnit=RRU.*')
for proxy in results:
    print("proxy", proxy)