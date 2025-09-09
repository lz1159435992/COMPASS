List *seed(List *rtable, Bitmapset *rels_used)
{
  deparse_namespace dpns;

  memset(&dpns, 0, sizeof(dpns));
  dpns.rtable = rtable;
  dpns.subplans = NIL;
  dpns.ctes = NIL;
  dpns.appendrels = NULL;
  // ...
}

List *mutant(List *rtable, Bitmapset *rels_used)
{
  deparse_namespace dpns;

  memset(&dpns, 0, sizeof(dpns));
  dpns.rtable = NULL;
  dpns.subplans = NIL;
  dpns.rtable = rtable;
  dpns.ctes = NIL;
  dpns.appendrels = NULL;
  // ...
}