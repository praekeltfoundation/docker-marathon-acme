#!/usr/bin/env python
import os
import subprocess
import sys
import tempfile
import unittest

# NOTE: these tests don't really work on Docker for Mac. There are two issues:
# * `docker run` commands have a *lot* more latency on Docker for Mac and often
#   time out... even with 60 seconds of leeway.
# * The location that Python creates temporary directories isn't (by default)
#   shared with Docker containers.
DEFAULT_TIMEOUT = 60  # Seconds

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
        completed_process = run_container(
            '/tmp', '-a', 'https://acme-staging.api.letsencrypt.org/directory')
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
        uid, gid = os.getuid(), os.getgid()
        # Make sure we're not running as root so the test makes sense
        assert uid != 0

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = os.path.abspath(tmpdir)
            run_container(
                '-a', 'https://acme-staging.api.letsencrypt.org/directory',
                '/var/lib/marathon-acme',
                docker_opts=[
                    '-e', 'MARATHON_ACME_USER=%s:%s' % (uid, gid),
                    '-v', '%s:/var/lib/marathon-acme' % (tmpdir,),
                ]
            )

            # Check the files written have the correct owner
            client_key = os.path.join(tmpdir, 'client.key')
            self.assertTrue(os.path.exists(client_key))

            stat = os.stat(client_key)
            self.assertEqual(stat.st_uid, uid)
            self.assertEqual(stat.st_gid, gid)


if __name__ == '__main__':
    # FIXME: Is there a nicer way? :-(
    if len(sys.argv) < 2:
        print('usage:', sys.argv[0], 'IMAGE [UNITTEST_ARGS]')
        print('  where IMAGE is the Docker image tag to test, and')
        print('        UNITTEST_ARGS are any arguments to pass to unittest')
        sys.exit(1)

    image = sys.argv[1]

    unittest.main(argv=[sys.argv[0]] + sys.argv[2:])
