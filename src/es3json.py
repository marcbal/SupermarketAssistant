# Copyright (c) 2024 Marc Baloup
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re, yaml

def load_es3_json_file(path):
    """Loads a JSON encoded ES3 ('Easy save 3') file.
    May badly interpret strings containing tabs or the '([0-9]+):' pattern."""
    with open(path, encoding="utf-8") as fp:
        raw = fp.read()
    # The file is in JSON format, but not exactly: ES3 ('Easy save 3'
    # from Unity Asset Store) does not wrap int keys of objects into
    # double quotes, so this is not technically valid JSON. It turns
    # out that JSON is almost a subset of the YAML specs, that accepts
    # unquoted keys. But we still have to convert the imput data to make it
    # fully YAML complient: replace tabs with spaces and put a space after
    # a column for integer keys
    raw = raw.replace("\t", " ") # removing tabs
    raw = re.sub(r"([0-9]+):", "\\1: ", raw) # add space after ":"
    return yaml.load(raw, yaml.SafeLoader) # treating bad JSON as YAML