import os
import nose.tools as nt
import test_IODriver as parent


class TestFileInputDriver(parent.TestIODriver):
    r"""Test runner for FileInputDriver.

    Attributes (in addition to parent class's):
        filepath (str): Full path to test file.

    """

    def __init__(self):
        super(TestFileInputDriver, self).__init__()
        self.driver = 'FileInputDriver'
        self.filepath = os.path.abspath('ascii_input.txt')
        self.args = self.filepath
        self.attr_list += ['args', 'fd', 'lock']

    def setup(self):
        r"""Create a driver instance and start the driver."""
        with open(self.filepath, 'wb') as fd:
            fd.write(self.file_contents)
        super(TestFileInputDriver, self).setup()

    def teardown(self):
        r"""Remove the instance, stoppping it."""
        super(TestFileInputDriver, self).teardown()
        if os.path.isfile(self.filepath):
            os.remove(self.filepath)

    def assert_before_stop(self):
        r"""Assertions to make before stopping the driver instance."""
        super(TestFileInputDriver, self).assert_before_stop()
        msg_recv = self.instance.recv_wait()
        nt.assert_equal(msg_recv, self.file_contents)

    def assert_after_terminate(self):
        r"""Assertions to make after stopping the driver instance."""
        super(TestFileInputDriver, self).assert_after_terminate()
        assert(self.instance.fd is None)
        
    def test_send_recv(self):
        r"""Test sending/receiving small message."""
        pass
        # data = self.instance.recv_wait()
        # super(TestFileInputDriver, self).test_send_recv()

    def test_send_recv_nolimit(self):
        r"""Test sending/receiving large message."""
        pass
        # data = self.instance.recv_wait_nolimit()
        # super(TestFileInputDriver, self).test_send_recv_nolimit()
