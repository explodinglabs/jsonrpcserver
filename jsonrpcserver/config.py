"""
Import this module to configure the package::

    from jsonrpcserver import config
    config.debug = True
"""
#: Convert any camelCase keys in a request to snake_case before processing.
#: Saves time by cleaning up key names for you. *Recommended*
convert_camel_case = False

#: Include more information in error messages.
debug = False

#: Log requests
log_requests = True

#: Log responses
log_responses = True

#: Respond to notifications with errors. The JSON-RPC specification says
#: notifications should not be responded to, so enabling this breaks the spec.
#: But I prefer to know if there was an error.
notification_errors = False

#: Validate requests against the JSON-RPC schema. Disable to speed up
#: processing.
schema_validation = True
