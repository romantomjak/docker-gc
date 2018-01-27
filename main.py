import argparse
import re
import subprocess
import sys

DOCKER_VERSION = 17


def run(cmd, check=True, stdout=subprocess.PIPE, split=True):
    """Run command and return it's output."""
    try:
        p = subprocess.run(cmd, check=check, stdout=stdout)
        output = p.stdout.decode('utf-8')
        if split:
            return output.split("\n")[1:-1]
        return output
    except subprocess.CalledProcessError as e:
        print(e)
        sys.exit(1)


def check_docker_version():
    """Check that Docker version is no less than DOCKER_VERSION."""
    try:
        stdout = run(["docker", "--version"], split=False)
        match = re.search(r'(\d+)\.(\d+)', stdout)

        if not match:
            raise ValueError("Could not determine docker version")

        major, minor = match.groups(0)

        if int(major) < DOCKER_VERSION:
            raise ValueError("Unsupported docker version {}.{}, minimum version {}".format(major, minor, DOCKER_VERSION))
    except ValueError as e:
        print(e)
        sys.exit(1)


def is_excluded(repo, excluded):
    """Check if repo should be included."""
    if not excluded:
        return False
    return any([r.strip() in repo for r in excluded[0].split(",")])


def untag(dry_run, keep, excluded):
    """Leaves only up to 'KEEP' images per repo."""
    stdout = run(["docker", "image", "ls", "--format", "{{.Repository}}  {{.Tag}}"])

    regex = re.compile(r'\s{2,}')
    repos = {}
    to_remove = set()
    for line in stdout:
        repo_name, tag = regex.split(line)

        if repo_name == '<none>':
            continue

        if is_excluded("{}:{}".format(repo_name, tag), excluded):
            continue

        num_tags = repos.get(repo_name, 0)
        if num_tags < keep:
            repos[repo_name] = num_tags + 1
        else:
            to_remove.add("{}:{}".format(repo_name, tag))

    if to_remove:
        for image in to_remove:
            if dry_run:
                print("Untagged:", image)
            else:
                print(run(["docker", "image", "rm", image], split=False))

    return to_remove


def remove_dangling(dry_run, untagged):
    """Runs Docker's built-in command for removing dangling images."""
    if dry_run:
        stdout = run(["docker", "image", "ls", "--filter", "dangling=true", "--format", "{{.Repository}}  {{.Tag}}"])

        regex = re.compile(r'\s{2,}')
        to_remove = set()
        for line in stdout:
            repo_name, tag = regex.split(line)
            to_remove.add("{}:{}".format(repo_name, tag))

        images = untagged | to_remove

        if images:
            for image in images:
                print("Deleted:", image)
    else:
        run(["docker", "system", "prune", "-f"])


def main():
    parser = argparse.ArgumentParser(description='Docker image garbage collector')
    parser.add_argument('--keep', dest='keep', default=5, metavar="NUM",
                        help='keep up to NUM images (default: %(default)s)')
    parser.add_argument('--exclude', dest='exclude', nargs='*', type=str, metavar="repo,repo",
                        help='exclude repos from garbage collection')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                        help='do a dry run without actually deleting anything')
    args = parser.parse_args()

    check_docker_version()

    untagged = untag(args.dry_run, int(args.keep), args.exclude)

    remove_dangling(args.dry_run, untagged)


if __name__ == '__main__':
    main()
