.. rubric::
    `jsonrpcserver <index.html>`_

API
***

.. automodule:: dispatcher
    :members:

.. automodule:: response
.. autoclass:: RequestResponse
    :members:
    :inherited-members:
    :member-order: alphabetical

.. autoclass:: NotificationResponse
    :members:
    :inherited-members:
    :member-order: alphabetical

.. autoclass:: ErrorResponse
    :members:
    :inherited-members:
    :member-order: alphabetical

.. automodule:: methods
    :members:

.. automodule:: jsonrpcserver.exceptions

    .. autoexception:: ParseError
        :show-inheritance:
        :members:
        :undoc-members:
        :member-order: bysource

    .. autoexception:: InvalidRequest
        :show-inheritance:
        :members:
        :undoc-members:
        :member-order: bysource

    .. autoexception:: MethodNotFound
        :show-inheritance:
        :members:
        :undoc-members:
        :member-order: bysource

    .. autoexception:: InvalidParams
        :show-inheritance:
        :members:
        :undoc-members:
        :member-order: bysource

    .. autoexception:: ServerError
        :show-inheritance:
        :members:
        :undoc-members:
        :member-order: bysource
