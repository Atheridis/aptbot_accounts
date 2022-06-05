# Restructure

There should be a higher focus on using packages over namespaces. This could
potentially solve a lot of current issues.

Another focus should be on unit tests. It shouldn't be too hard to implement them,
and they will make debugging much easier.

--------------

## Change how commands are handled

Commands are currently handled by having a prefix, then sending the message over.
Commands should instead use a utility like shlex (Simple lexical analysis).
A user should use a symbol like `!`, `?`, `\`, `#`, etc. to invoke the bot, then
start a command and add options, similarly to how a cli tool would be used on
Unix systems.

One symbol could potentially invoke the bot normally `?` and one could be used
for elevated privileges `\`.

Finally each command should have well written documentation which can be invoked
through either a help option `?command --help` or a help command `?help command`.

--------------

## Use SQLAlchemy for handling databases

Databases are handled using sqlite3, changing over to SQLAlchemy will reduce errors
and allow to change to another database if necessary in the future. All tables
should also in the same database.

--------------

## Reconsider the way commands and auto_messages are imported as modules

Currently commands and auto_messages are mass imported by globbing through
their directories. They use the python module name as the command name and invoke
the `main` method. This method is quite ugly and should be reconsidered.

--------------

## Advanced permission system with roles

The permission system in use is to assign all users with an integer, the lower
the number, the higher their permissions. A user can only use commands with
a permission number higher than or equal to their own permission number.
While this linear system works fine, a more advanced system with roles will
allow for a lot more freedom.

--------------

## Simple Variable Management System

Holding on to data which can be used or changed by other commands is very useful.
