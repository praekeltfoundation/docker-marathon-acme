#!/usr/bin/env python
import argparse
import os
import subprocess
import sys
import tempfile
import unittest

DEFAULT_TIMEOUT = 30  # Seconds
image = None


def run_container(*args, docker_opts=[]):
    run_args = ['docker', 'run', '--rm'] + docker_opts + [image] + list(args)
    # Requires Python 3.5+
    return subprocess.run(
        run_args,
        timeout=DEFAULT_TIMEOUT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )


class TestEntrypoint(unittest.TestCase):
    def test_no_args(self):
        """
        When the container is run with no arguments, marathon-acme should start
        and the storage directory should default to /var/lib/marathon-acme.
        """
        completed_process = run_container()
        # marathon-acme started...
        self.assertRegex(completed_process.stdout, r'Running marathon-acme')
        # The storage-dir defaulted to /var/lib/marathon-acme
        self.assertRegex(completed_process.stdout, r'/var/lib/marathon-acme')
        # There was some error message
        self.assertRegex(completed_process.stderr, r'error')

        # FIXME: Apparently the returncode is 0 :/
        self.assertEqual(completed_process.returncode, 0)

    def test_first_argument_is_option(self):
        """
        When the container is run and its first argument looks like an option,
        marathon-acme should be run with that option.
        """
        completed_process = run_container('--help')
        self.assertRegex(completed_process.stdout, r'usage: marathon-acme')
        self.assertEqual(completed_process.stderr, '')
        self.assertEqual(completed_process.returncode, 0)

    def test_first_argument_is_directory(self):
        """
        When the container is run and its first argument looks like a path to a
        directory, marathon-acme should be run with that path as an argument.
        """
        completed_process = run_container('/tmp')
        # marathon-acme started...
        self.assertRegex(completed_process.stdout, r'Running marathon-acme')
        # The storage-dir is set to /tmp
        self.assertRegex(completed_process.stdout, r'/tmp')
        # There was some error message
        self.assertRegex(completed_process.stderr, r'error')

        # FIXME: Apparently the returncode is 0 :/
        self.assertEqual(completed_process.returncode, 0)

    def test_other_command(self):
        """
        When the container is run with arguments that look like some other
        non-marathon-acme command, that command should be run.
        """
        completed_process = run_container('echo', 'foo')
        self.assertEqual(completed_process.stdout, 'foo\n')
        self.assertEqual(completed_process.stderr, '')
        self.assertEqual(completed_process.returncode, 0)

    def test_switch_user(self):
        """
        When the MARATHON_ACME_USER environment variable is set, marathon-acme
        should change to the specified user when running and files created
        should be owned by the user.
        """
        # Assume we're not running the tests as root
        user = '%s:%s' % (os.getuid(), os.getgid())
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = os.path.abspath(tmpdir)
            run_container(docker_opts=[
                '-e', 'MARATHON_ACME_USER=%s' % (user,),
                '-v', '%s:/var/lib/marathon-acme' % (tmpdir,),
            ])

            # Check the files written have the correct owner
            client_key = os.path.join(tmpdir, 'client.key')
            self.assertTrue(os.path.exists(client_key))

            stat = os.stat(client_key)
            self.assertEqual(stat.st_uid, os.getuid())
            self.assertEqual(stat.st_gid, os.getgid())


if __name__ == '__main__':
    # FIXME: Is there a nicer way? :-(
    parser = argparse.ArgumentParser()
    parser.add_argument('image', help='the image to test')
    args = parser.parse_args()
    image = args.image

    raw_args = list(sys.argv)
    del raw_args[1]
    unittest.main(argv=raw_args)
