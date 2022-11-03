################
Installation
################

.. contents:: Table of Contents


*********************
Package Requirements
*********************

.. literalinclude:: ../../../requirements/requirements.in

****************
CI Requirements
****************

.. literalinclude:: ../../../requirements/requirements_dev.in

*************
Installation
*************

From pypi server

.. code-block:: bash

    pip install py4ai-config

From source

.. code-block:: bash

    git clone https://github.com/NicolaDonelli/py4ai-config
    cd "$(basename "https://github.com/NicolaDonelli/py4ai-config" .git)"
    make install
