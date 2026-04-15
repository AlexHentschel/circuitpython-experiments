# -*- coding: utf-8 -*-
"""Basic functionality of CircuitPython kernel."""
import ast
import logging
import re
import time

from ipykernel.kernelbase import Kernel
from serial.serialutil import SerialException
from .board import Board, BoardError
from .version import __version__

# Create global KERNEL_LOGGER for debug messages.
KERNEL_LOGGER = logging.getLogger(__name__)


class CircuitPyKernel(Kernel):
    """CircuitPython kernel implementation."""

    protocol_version = '4.5.2'
    implementation = 'circuitpython_kernel'
    implementation_version = __version__
    language_info = {
        'name': 'python',
        'version': '3',
        'mimetype': 'text/x-python',
        'file_extension': '.py',
        'pygments_lexer': 'python3',
        'codemirror_mode': {'name': 'python', 'version': 3},
    }
    banner = "CircuitPython"
    help_links = [
        {
            'text': 'CircuitPython kernel',
            'url': 'https://github.com/adafruit/circuitpython_kernel',
        }
    ]

    def __init__(self, **kwargs):
        """Set up connection to board"""
        super().__init__(**kwargs)
        KERNEL_LOGGER.debug(f"circuitpython_kernel version {__version__}")
        self.board = Board()
        self.upload_delay = 0.06

    def is_magic(self, line):
        """Returns true if line was handled"""
        if line.startswith("%softreset"):
            self.board.softreset()
        elif line.startswith("%upload_delay"):
            try:
                s_line = line.split(' ')
                self.upload_delay = float(s_line[1])
                KERNEL_LOGGER.debug(f"upload_delay set to {float(s_line[1])} s")
            except TypeError:
                pass
        elif line.startswith("%python"):
            #python line magic, runs what ever is on the line following the %python magic.
            code = line.lstrip("%python")
            code = code.lstrip(' ')
            for item in code.split(";"):
                item = item.lstrip(' ') #remove leading white space
                try:
                    print(eval(item))   #does not print
                except:
                    out = exec(item)
                    if out != None:
                        print(out)      #does not print
            
        else:
            return False
        return True

    def is_cell_magic(self, code):
        """Cell magic to run python code.
        -----
        Cell shall begin with %%python followed by a new line
        Will iteratively run each line of code.
        """

        if code.startswith("%%python"):
            code = code.lstrip("%%python")
            code = code.lstrip(' ')
            data = code.splitlines(True)
            for item in data:
                
                code = code.lstrip(' ')    #this removes all preceeding white space, 
                                           #i need to figure out how to get for loops, etc working
                try:
                    print(eval(item))      #does not print
                except:
                    out = exec(item)

                    if out != None:
                        print(out)         #does not print
            return True
        else:
            return False

    @classmethod
    def is_comment(cls, line):
        """Returns true if the line of code is empty or a comment.

            It is much faster to check and skip these lines on the host then
            to send them to the MCU (with an `upload_delay` between each one).
        """
        line = line.strip()
        return len(line) == 0 or line.startswith("#")

    def run_code(self, code):
        """Run a code snippet.

        Parameters
        ----------
        code : str
            Code to be executed.

        Returns
        -------
        out
            Decoded bytearray output result from code run.
        err
            Decoded bytearray error from code run.

        """
        # make sure we are connected to the board
        self.board.connect()
        ##cell check for python cell magics
        python_cell = self.is_cell_magic(code)
    
        if python_cell == True:
            out = []
            err = []
            return out, err
        # Send code to board & fetch results (if any) after each line sent
        for line in code.splitlines(False):
            if not self.is_magic(line) and not self.is_comment(line):
                self.board.write(line.encode('utf-8'))
                self.board.write(b'\r\n')
                # The Featherboard M4 cannot keep up with long code cells
                time.sleep(self.upload_delay)
        # Kick off evaluation ...
        self.board.write(b'\r\x04')   # Control-D
        # Set up a bytearray to hold the result from the code run
        result = bytearray()
        while not result.endswith(b'\x04>'):  # Control-D
            time.sleep(0.1)
            result.extend(self.board.read_all())
        KERNEL_LOGGER.debug('received: %s', result.decode('utf-8', 'replace'))

        assert result.startswith(b'OK')
        out, err = result[2:-2].split(b'\x04', 1)  # split result

        return out.decode('utf-8', 'replace'), err.decode('utf-8', 'replace')

    def do_execute(self, code, silent, store_history=True,
                                  user_expressions=None, allow_stdin=False):
        """Execute a user's code cell.

        Parameters
        ----------
        code : str
            Code, one or more lines, to be executed.
        silent : bool
            True, signals kernel to execute code quietly, and output is not
            displayed.
        store_history : bool
            Whether to record code in history and increase execution count. If
            silent is True, this is implicitly false.
        user_expressions : dict, optional
            Mapping of names to expressions to evaluate after code is run.
        allow_stdin : bool
            Whether the frontend can provide input on request (e.g. for
            Python’s raw_input()).

        Returns
        -------
        dict
            Execution results.

        """
        if not code.strip():
            return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {}}
        # evaluate code on board
        out = err = None
        try:
            out, err = self.run_code(code)
        except (BoardError, SerialException) as ser_eror:
            KERNEL_LOGGER.debug(f'no connection {ser_eror}')
            err = f"No connection to CiruitPython VM: {ser_eror}"
        except KeyboardInterrupt:
            KERNEL_LOGGER.debug(f'keyboard interrupt')
            err = "Keyboard Interrupt"
        if out:
            KERNEL_LOGGER.debug(f"Output: '{out}'")
        if err:
            KERNEL_LOGGER.debug(f"Error:  '{err}'")
        if not silent:
            out_content = {'name': 'stdout', 'text': out}
            err_content = {'name': 'stderr', 'text': err}
            if out:
                self.send_response(self.iopub_socket, 'stream', out_content)
            if err:
                self.send_response(self.iopub_socket, 'stream', err_content)

        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }

    def _eval(self, expr):
        """Evaluate the expression.

        Use ast's literal_eval to prevent strange input from execution.

        """
        try:
            out, err = self.run_code('print({})'.format(expr))
        except (BoardError, SerialException) as ser_eror:
            out = err = f"Lost connection to CiruitPython VM: {ser_eror}"
        KERNEL_LOGGER.debug('Output: %s', out)
        KERNEL_LOGGER.debug('Error %s', err)
        return ast.literal_eval(out)

    def do_shutdown(self, restart):
        """Handle the kernel shutting down."""
        KERNEL_LOGGER.debug('Shutting down CircuitPython Board Connection..')

        # If we try to disconnect before sending any commands, the `write()`
        # call here will fail. So, make sure we are connected to the board.
        self.board.connect()
        self.board.write(b'\r\x02')

        KERNEL_LOGGER.debug('closing board connection..')
        self.board.close()

    def do_complete(self, code, cursor_pos):
        """Support code completion."""
        code = code[:cursor_pos]
        match = re.search(r'(\w+\.)*(\w+)?$', code)
        if match:
            prefix = match.group()
            if '.' in prefix:
                obj, prefix = prefix.rsplit('.')
                names = self._eval('dir({})'.format(obj))
            else:
                names = self._eval('dir()')
            matches = [n for n in names if n.startswith(prefix)]
            return {
                'matches': matches,
                'cursor_start': cursor_pos - len(prefix),
                'cursor_end': cursor_pos,
                'metadata': {},
                'status': 'ok',
            }

        else:
            return {
                'matches': [],
                'cursor_start': cursor_pos,
                'cursor_end': cursor_pos,
                'metadata': {},
                'status': 'ok',
            }
