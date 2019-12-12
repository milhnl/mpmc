mpmc - minimal python matrix client
===================================

This is a very small [matrix](https://matrix.org) client. It aims
to allow you to send and receive messages using an interface you
can write yourself. Examples can be found
[here](https://gitlab.com/meutraa/mm).

Installation
------------

    pip3 install --user "matrix-nio"
    sudo make install

On my macOS I had to jump through some more hoops. I hope to automate
this via the Makefile or something like that in the future. If you
want to use this now, just ask me for help if you can not figure
it out.

Usage
-----
It's almost the same as [mm](https://gitlab.com/meutraa/mm), with one
small incompatibility for safety: passwords should be passed as a
command. The example below is how you *shouldn't* do it. Use `pass`,
or your system keyring.

    mpmc -u @name:example.org -h https://example.org -p 'echo hunter2'

Why this client?
----------------
This is a re-implementation of [mm](https://gitlab.com/meutraa/mm)
in Python. `mm` does not support end-to-end encryption, and probably
never will. This is due to the library it uses, which isn't really
maintained anymore either. Python is not the ideal choice for minimal
software, but it gets the job done, and is the only language at the
moment with an e2e-enabled matrix client library.
