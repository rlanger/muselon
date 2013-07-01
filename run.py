#!/usr/bin/env python
import os
from muselon import muselon

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    muselon.run(host='0.0.0.0', port=port, debug=True)