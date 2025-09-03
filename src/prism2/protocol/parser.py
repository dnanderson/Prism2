import collections

# A simple, example-driven protocol definition.
# In a real application, this would be more robust and likely loaded from a config file.
# The key is the first byte of the command.
PROTOCOL_DEFINITIONS = {
    "01": {
        "name": "Read Status Register",
        "fields": collections.OrderedDict([
            ("Command", 1),
            ("Dummy Byte", 1),
        ]),
        "response": collections.OrderedDict([
            ("Status", 1),
            ("Dummy Byte", 1),
        ])
    },
    "06": {
        "name": "Write Enable",
        "fields": collections.OrderedDict([
            ("Command", 1),
        ]),
        "response": collections.OrderedDict([]) # No response data expected
    },
    "C7": {
        "name": "Chip Erase",
        "fields": collections.OrderedDict([
            ("Command", 1),
        ]),
        "response": collections.OrderedDict([]) # No response data expected
    },
    "default": {
        "name": "Unknown Command",
        "fields": collections.OrderedDict([
            ("Data", -1) # -1 means "the rest of the data"
        ]),
        "response": collections.OrderedDict([
            ("Data", -1)
        ])
    }
}

def parse_hex_data(hex_string, is_command):
    """
    Parses a hex string into a human-readable breakdown based on the protocol.

    Args:
        hex_string (str): The hex data to parse.
        is_command (bool): True if parsing a command, False for a response.

    Returns:
        A formatted string with the breakdown of the fields.
    """
    if not hex_string:
        return "No data to parse."

    data_bytes = bytes.fromhex(hex_string)

    # Determine the protocol definition to use
    cmd_byte_hex = hex_string[:2].upper()
    definition = PROTOCOL_DEFINITIONS.get(cmd_byte_hex, PROTOCOL_DEFINITIONS["default"])

    # Select the correct field map (command or response)
    field_map = definition["fields"] if is_command else definition["response"]

    if not field_map:
        return f"{definition['name']} (Response)\n - No response fields defined."

    breakdown_lines = [f"{definition['name']} ({'Command' if is_command else 'Response'})"]

    byte_cursor = 0
    for field_name, field_len in field_map.items():
        if field_len == -1: # "The rest of the data"
            field_data = data_bytes[byte_cursor:]
            byte_cursor = len(data_bytes)
        else:
            field_data = data_bytes[byte_cursor : byte_cursor + field_len]
            byte_cursor += field_len

        if not field_data:
            break

        field_hex = field_data.hex().upper()
        breakdown_lines.append(f" - {field_name} ({len(field_data)}B): 0x{field_hex}")

    if byte_cursor < len(data_bytes):
        remaining_data = data_bytes[byte_cursor:].hex().upper()
        breakdown_lines.append(f" - Unparsed Data: 0x{remaining_data}")

    return "\n".join(breakdown_lines)
