def text_to_bin(text):
    """Convert text to binary string."""
    return ''.join(format(ord(char), '08b') for char in text)

def bin_to_text(binary):
    """Convert binary string to text."""
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join(chr(int(c, 2)) for c in chars)