"""
Configuration
*************
Import ``config`` to configure various settings, for example::

    from jsonrpcserver import config
    config.debug = True
"""
#: Include more information in error messages.
debug = False

#: Validate requests against the schema. Disable to speed up processing.
schema_validation = True

#: Respond to notifications with errors. The JSON-RPC specification says
#: notifications should not be responded to, so enabling this breaks the spec.
#: But I prefer to know if there was an error.
notification_errors = False

#: Convert any camelCase keys in a request to under_score before processing.
#: This saves time by cleaning up messy key names for you. *Recommended*
convert_camel_case = False
