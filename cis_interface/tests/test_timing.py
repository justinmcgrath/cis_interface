import os
import copy
import nose.tools as nt
from cis_interface import tools, timing, backwards, platform
from cis_interface.tests import CisTestClass


_test_size = 1
_test_count = 1
_test_nrep = 1
_test_lang = 'c'
# On windows, it's possible to not have a C/C++ communication library installed
if 'c' not in timing._lang_list:  # pragma: windows
    _test_lang = 'python'
# _test_run = timing.TimedRun(_test_lang, _test_lang)
# _test_run.time_run(_test_count, _test_size, nrep=_test_nrep)
_this_platform = (platform._platform,
                  backwards._python_version,
                  tools.get_default_comm())
_base_environment = {'platform': 'Linux',
                     'python_ver': '2.7',
                     'comm_type': 'ZMQComm'}
_valid_platforms = [('Linux', '2.7', 'ZMQComm'),
                    ('Linux', '2.7', 'IPCComm'),
                    ('Linux', '3.5', 'ZMQComm'),
                    ('MacOS', '2.7', 'ZMQComm'),
                    ('Windows', '2.7', 'ZMQComm')]
_testfile_json = 'test_run123.json'
_testfile_dat = 'test_run123.dat'


def test_get_source():
    r"""Test getting source file for test."""
    lang_list = timing._lang_list
    dir_list = ['src', 'dst']
    for l in lang_list:
        for d in dir_list:
            fname = timing.get_source(l, d)
            assert(os.path.isfile(fname))


def test_platform_error():
    r"""Test error when test cannot be performed."""
    if platform._is_mac:
        test_platform = 'Linux'
    else:
        test_platform = 'MacOS'
    x = timing.TimedRun(_test_lang, _test_lang, platform=test_platform)
    nt.assert_raises(RuntimeError, x.can_run, raise_error=True)


class TimedRunTestBase(CisTestClass):
    r"""Base test class for the TimedRun class."""

    _mod = 'cis_interface.timing'
    _cls = 'TimedRun'
    test_name = 'timed_pipe'
    _filename = None
    platform = None
    python_ver = None
    comm_type = None
    dont_use_perf = False
    language = _test_lang
    count = 1
    size = 1
    nrep = 1

    @property
    def inst_args(self):
        r"""list: Arguments for creating a class instance."""
        return [self.language, self.language]

    @property
    def inst_kwargs(self):
        r"""dict: Keyword arguments for creating a class instance."""
        return {'test_name': self.test_name, 'filename': self._filename,
                'platform': self.platform, 'python_ver': self.python_ver,
                'comm_type': self.comm_type, 'dont_use_perf': self.dont_use_perf}

    @property
    def time_run_args(self):
        r"""tuple: Arguments for time_run."""
        return (self.count, self.size)

    @property
    def time_run_kwargs(self):
        r"""dict: Keyword arguments for time_run."""
        return {'nrep': self.nrep}

    @property
    def entry_name(self):
        r"""str: Name of the entry for the provided time_run_args."""
        return self.instance.entry_name(*self.time_run_args)

    @property
    def filename(self):
        r"""str: Name of the file where data is stored."""
        return self.instance.filename

    def get_raw_data(self):
        r"""Get the raw contents of the data file."""
        out = ''
        if os.path.isfile(self.filename):
            with open(self.filename, 'r') as fd:
                out = fd.read()
        return out

    def time_run(self):
        r"""Perform a timed run."""
        self.instance.time_run(*self.time_run_args, **self.time_run_kwargs)


class TestTimedRun(TimedRunTestBase):
    r"""Test class for the TimedRun class using existing data."""

    platform = _base_environment['platform']
    python_ver = _base_environment['python_ver']
    comm_type = _base_environment['comm_type']
    language = 'python'

    @property
    def count(self):
        r"""int: Number of messages to use for tests."""
        return self.instance.base_msg_count

    @property
    def size(self):
        r"""int: Size of messages to use for tests."""
        return self.instance.base_msg_size
    
    def test_json(self):
        r"""Test loading/saving perf data as json."""
        old_text = self.get_raw_data()
        x = self.instance.load(as_json=True)
        self.instance.save(x, overwrite=True)
        new_text = self.get_raw_data()
        nt.assert_equal(new_text, old_text)

    def test_save(self):
        r"""Test save with/without overwrite."""
        old_text = self.get_raw_data()
        nt.assert_raises(RuntimeError, self.instance.save, self.instance.data)
        self.instance.save(self.instance.data, overwrite=True)
        new_text = self.get_raw_data()
        nt.assert_equal(new_text, old_text)

    def test_scaling_count(self):
        r"""Test running scaling with number of messages."""
        kwargs = dict(min_count=self.count, max_count=self.count,
                      nsamples=1, nrep=self.nrep)
        self.instance.scaling_count(self.size, scaling='log', **kwargs)
        self.instance.scaling_count(self.size, scaling='linear',
                                    per_message=True, **kwargs)
        nt.assert_raises(ValueError, self.instance.scaling_count, self.size,
                         scaling='invalid')

    def test_scaling_size(self):
        r"""Test running scaling with size of messages."""
        kwargs = dict(min_size=self.size, max_size=self.size,
                      nsamples=1, nrep=self.nrep)
        self.instance.scaling_size(self.count, scaling='log', **kwargs)
        self.instance.scaling_size(self.count, scaling='linear',
                                   per_message=True, **kwargs)
        nt.assert_raises(ValueError, self.instance.scaling_size, self.count,
                         scaling='invalid')

    def test_plot_scaling_joint(self):
        r"""Test plot_scaling_joint."""
        kwargs = dict(msg_size0=self.size, msg_count0=self.count,
                      msg_size=[self.size], msg_count=[self.count],
                      per_message=True, time_method='bestof')
        self.instance.plot_scaling_joint(**kwargs)

    def test_plot_scaling(self):
        r"""Test plot_scaling corner cases not covered by test_plot_scaling_joint."""
        self.instance.plot_scaling(self.size, [self.count], per_message=True,
                                   time_method='average', yscale='linear')
        self.instance.plot_scaling([self.size], self.count, per_message=False,
                                   time_method='average', yscale='log')

        if False:
            # Test with msg_count on x linear/linear axs
            args = (self.size, [self.count])
            kwargs = {'axs': None, 'nrep': self.nrep,
                      'time_method': 'average', 'per_message': True}
            kwargs['axs'] = self.instance.plot_scaling(*args, **kwargs)
            kwargs['time_method'] = 'bestof'
            kwargs['axs'] = self.instance.plot_scaling(*args, **kwargs)
            # Test with msg_size on x log/log axes
            args = ([self.size], self.count)
            kwargs = {'axs': None, 'nrep': self.nrep, 'time_method': 'average',
                      'xscale': 'log', 'yscale': 'log'}
            kwargs['axs'] = self.instance.plot_scaling(*args, **kwargs)
            kwargs['time_method'] = 'bestof'
            kwargs['axs'] = self.instance.plot_scaling(*args, **kwargs)
        # Errors
        nt.assert_raises(RuntimeError, self.instance.plot_scaling,
                         [self.size], [self.count])
        nt.assert_raises(RuntimeError, self.instance.plot_scaling,
                         self.size, self.count)
        nt.assert_raises(ValueError, self.instance.plot_scaling,
                         [self.size], self.count, nrep=self.nrep,
                         time_method='invalid')

    def test_perfjson_to_pandas(self):
        r"""Test perfjson_to_pandas."""
        timing.perfjson_to_pandas(self.filename)

    def test_fits(self):
        r"""Test fits to scaling on one platform."""
        self.instance.time_per_byte
        self.instance.time_per_message
        self.instance.startup_time

    def test_plot_scalings(self):
        r"""Test plot_scalings corner cases on test platform."""
        kwargs = copy.deepcopy(self.inst_kwargs)
        kwargs.update(msg_size=[self.size], msg_size0=self.size,
                      msg_count=[self.count], msg_count0=self.count,
                      cleanup_plot=True)
        for c in ['comm_type', 'language', 'platform', 'python_ver']:
            ikws = copy.deepcopy(kwargs)
            ikws['compare'] = c
            if c in ikws:
                del ikws[c]
            if c == 'language':
                ikws['per_message'] = True
                ikws['compare_values'] = [self.language]
            timing.plot_scalings(**ikws)
        # Errors
        nt.assert_raises(ValueError, timing.plot_scalings, compare='invalid')
        nt.assert_raises(RuntimeError, timing.plot_scalings, compare='comm_type',
                         comm_type='ZMQComm')

    def test_production_runs(self):
        r"""Test production tests (those used in paper)."""
        # Limit language list for tests
        for c in ['comm_type', 'language', 'platform', 'python_ver']:
            kwargs = copy.deepcopy(self.inst_kwargs)
            kwargs.update(compare=c, cleanup_plot=True, use_paper_values=True)
            if c in kwargs:
                del kwargs[c]
            timing.plot_scalings(**kwargs)
            # Also do MacOS plot w/ Matlab
            if c == 'language':
                kwargs['platform'] = 'MacOS'
                timing.plot_scalings(**kwargs)


class TestTimedRunTemp(TimedRunTestBase):
    r"""Test class for the TimedRun class using temporary data."""

    _filename = 'test_run123.json'

    @property
    def description_prefix(self):
        r"""String prefix to prepend docstr test message with."""
        out = super(TestTimedRunTemp, self).description_prefix
        out += ' Temporary'
        return out

    def cleanup_files(self):
        r"""Remove the temporary file if it exists."""
        if os.path.isfile(self.instance.filename):
            os.remove(self.instance.filename)
        if os.path.isfile(self.instance.perfscript):  # pragma: debug
            os.remove(self.instance.perfscript)

    def setup(self, *args, **kwargs):
        r"""Cleanup the file if it exists and then reload."""
        super(TestTimedRunTemp, self).setup(*args, **kwargs)
        self.cleanup_files()
        self.instance.reload()

    def teardown(self, *args, **kwargs):
        r"""Cleanup temporary files before destroying instance."""
        self.cleanup_files()
        super(TestTimedRunTemp, self).teardown(*args, **kwargs)

    @property
    def time_run_kwargs(self):
        r"""dict: Keyword arguments for time_run."""
        out = super(TestTimedRunTemp, self).time_run_kwargs
        out['overwrite'] = True
        return out

    def test_perf_func(self):
        r"""Test perf_func."""
        timing.perf_func(1, self.instance, self.count, self.size)

    def test_run_overwrite(self):
        r"""Test performing a run twice, the second time with ovewrite."""
        self.time_run()
        # Reload instance to test load for existing file
        self.clear_instance()
        self.time_run()
        self.instance.remove_entry(self.entry_name)
        assert(not self.instance.has_entry(self.entry_name))

    def test_languages(self):
        r"""Test different combinations of source/destination languages."""
        kwargs = copy.deepcopy(self.inst_kwargs)
        for l1 in timing._lang_list:
            args = (l1, l1)
            x = timing.TimedRun(*args, **kwargs)
            x.time_run(*self.time_run_args, **self.time_run_kwargs)

    def test_comm_types(self):
        r"""Test different comm types."""
        args = copy.deepcopy(self.inst_args)
        kwargs = copy.deepcopy(self.inst_kwargs)
        for c in timing._comm_list:
            kwargs['comm_type'] = c
            x = timing.TimedRun(*args, **kwargs)
            x.time_run(*self.time_run_args, **self.time_run_kwargs)


class TestTimedRunTempNoPerf(TestTimedRunTemp):
    r"""Test class for the TimedRun class using temporary data without perf."""

    _filename = None  # This forces use of standard name with .dat extension
    dont_use_perf = True

    @property
    def description_prefix(self):
        r"""String prefix to prepend docstr test message with."""
        out = super(TestTimedRunTempNoPerf, self).description_prefix
        out += ' (w/o perf)'
        return out

    def test_perf_func(self):
        r"""Disabled: Test perf_func."""
        pass

    def test_languages(self):
        r"""Disabled: Test different combinations of source/destination languages."""
        pass

    def test_comm_types(self):
        r"""Disabled: Test different comm types."""
        pass
