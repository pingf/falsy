===============
FAL.S.Y
===============


:Status: Alpha
:Author: Jesse MENG (dameng/pingf)
:Documentation: http://127.0.0.1/update_later


using falcon with swagger-ui and yaml!

:Basic Usage:

.. code-block:: python

    from falsy.falsy import FALSY

    f = FALSY(static_path='test', static_dir='static')
    f.begin_api()
    f.swagger('test.yml', ui=True,theme='impress')
    f.end_api()
    api = f.api


.. falsy: http://github.com

Installation
============

::

    pip install falsy


License
=======

Licensed under either of

* Apache License, Version 2.0,
  (./LICENSE-APACHE or http://www.apache.org/licenses/LICENSE-2.0)
* MIT license (./LICENSE-MIT or http://opensource.org/licenses/MIT)
  at your option.

------------
Contribution
------------

Unless you explicitly state otherwise, any contribution intentionally
submitted for inclusion in the work by you, as defined in the Apache-2.0
license, shall be dual licensed as above, without any additional terms or
conditions.