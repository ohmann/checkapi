#!/usr/sbin/dtrace -CZs
#pragma D option quiet
#pragma D option destructive

dtrace:::BEGIN
{
printf("We are tracing your files!â&#8364;¦ Hit Ctrl-C to end.\n");
}


/* filesystem */
syscall::creat:entry
{
printf("%Y\t", walltimestamp);
printf("%s (%d)\tuid %d\tcreated(%s, %03o)\n",
execname, pid, uid, stringof(copyinstr(arg0)), arg1);
@count_table[probefunc] = count() ;
}

syscall::open:entry
{
printf("%Y\t", walltimestamp);
printf("%s (%d)\tuid %d\t",execname, pid, uid);
printf("open: ");
trace(copyinstr(arg0));
printf("\n\n");
@count_table[probefunc] = count() ;
}

syscall::write:entry
/execname == "TextEdit"/ 
{ 
printf("%Y\t", walltimestamp);
printf("%s (%d)\tuid %d\twrite: ",execname, pid, uid);
trace(copyinstr(arg1)); 
printf("\n\n");
@count_table[probefunc] = count() ;
}


syscall::chmod:entry
{
printf("%Y\t", walltimestamp);
printf("%s (%d)\tuid %d\tchmod(%s, %03o)\n",
execname, pid, uid, stringof(copyinstr(arg0)), arg1);
@count_table[probefunc] = count() ;
}

syscall::chown:entry
{
printf("%Y\t", walltimestamp);
printf("%s (%d)\tuid %d\tchown(%s, %03o, %03o)\n",
execname, pid, uid, stringof(copyinstr(arg0)), arg1, arg2);
@count_table[probefunc] = count() ;
}

syscall::unlink:entry
{
printf("%Y\t", walltimestamp);
printf("%s (%d)\tuid %d\tdeleted(%s)\n",
execname, pid, uid, stringof(copyinstr(arg0)));
}
