import sys
from file import read_file, write_file  # assume you modularized your FAT functions

def nano(filename):
    if '.' not in filename:
        print("Usage: nano <filename.extension>")
        return

    name, extension = filename.split('.')
    data_bytes = read_file(name, extension)
    text = b''.join(data_bytes).decode('ascii', errors='ignore')

    print("----- FAT8 NANO -----")
    print("Editing:", filename)
    print("(Ctrl+D to save and exit)")

    # Show current content
    if text:
        print(text)

    # Read lines into buffer
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    new_text = '\n'.join(lines) + '\n'
    write_file(name, extension, list(new_text))

    print("Saved.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: nano <filename.extension>")
    else:
        nano(sys.argv[1])