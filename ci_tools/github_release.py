# a clone of the ruby example https://gist.github.com/valeriomazzeo/5491aee76f758f7352e2e6611ce87ec1
import os
from os import path

import re

import click
from click import Path
from github import Github, UnknownObjectException
# from valid8 import validate  not compliant with python 2.7


@click.command()
@click.option('-u', '--user', help='GitHub username')
@click.option('-p', '--pwd', help='GitHub password')
@click.option('-s', '--secret', help='GitHub access token')
@click.option('-r', '--repo-slug', help='Repo slug. i.e.: apple/swift')
@click.option('-cf', '--changelog-file', help='Changelog file path')
@click.option('-d', '--doc-url', help='Documentation url')
@click.option('-df', '--data-file', help='Data file to upload', type=Path(exists=True, file_okay=True, dir_okay=False,
                                                                          resolve_path=True))
@click.argument('tag')
def create_or_update_release(user, pwd, secret, repo_slug, changelog_file, doc_url, data_file, tag):
    """
    Creates or updates (TODO)
    a github release corresponding to git tag <TAG>.
    """
    # 1- AUTHENTICATION
    if user is not None and secret is None:
        # using username and password
        # validate('user', user, instance_of=str)
        assert isinstance(user, str)
        # validate('pwd', pwd, instance_of=str)
        assert isinstance(pwd, str)
        g = Github(user, pwd)
    elif user is None and secret is not None:
        # or using an access token
        # validate('secret', secret, instance_of=str)
        assert isinstance(secret, str)
        g = Github(secret)
    else:
        raise ValueError("You should either provide username/password OR an access token")
    click.echo("Logged in as {user_name}".format(user_name=g.get_user()))

    # 2- CHANGELOG VALIDATION
    regex_pattern = "[\s\S]*[\n][#]+[\s]*(?P<title>[\S ]*%s[\S ]*)[\n]+?(?P<body>[\s\S]*?)[\n]*?(\n#|$)" % re.escape(tag)
    changelog_section = re.compile(regex_pattern)
    if changelog_file is not None:
        # validate('changelog_file', changelog_file, custom=os.path.exists,
        #          help_msg="changelog file should be a valid file path")
        assert os.path.exists(changelog_file), "changelog file should be a valid file path"
        with open(changelog_file) as f:
            contents = f.read()

        match = changelog_section.match(contents).groupdict()
        if match is None or len(match) != 2:
            raise ValueError("Unable to find changelog section matching regexp pattern in changelog file.")
        else:
            title = match['title']
            message = match['body']
    else:
        title = tag
        message = ''

    # append footer if doc url is provided
    message += "\n\nSee [documentation page](%s) for details." % doc_url

    # 3- REPOSITORY EXPLORATION
    # validate('repo_slug', repo_slug, instance_of=str, min_len=1, help_msg="repo_slug should be a non-empty string")
    assert isinstance(repo_slug, str) and len(repo_slug) > 0, "repo_slug should be a non-empty string"
    repo = g.get_repo(repo_slug)

    # -- Is there a tag with that name ?
    try:
        tag_ref = repo.get_git_ref("tags/" + tag)
    except UnknownObjectException:
        raise ValueError("No tag with name %s exists in repository %s" % (tag, repo.name))

    # -- Is there already a release with that tag name ?
    click.echo("Checking if release %s already exists in repository %s" % (tag, repo.name))
    try:
        release = repo.get_release(tag)
        if release is not None:
            raise ValueError("Release %s already exists in repository %s. Please set overwrite to True if you wish to "
                             "update the release (Not yet supported)" % (tag, repo.name))
    except UnknownObjectException:
        # Release does not exist: we can safely create it.
        click.echo("Creating release %s on repo: %s" % (tag, repo.name))
        click.echo("Release title: '%s'" % title)
        click.echo("Release message:\n--\n%s\n--\n" % message)
        repo.create_git_release(tag=tag, name=title,
                                message=message,
                                draft=False, prerelease=False)

        # add the asset file if needed
        if data_file is not None:
            release = None
            while release is None:
                release = repo.get_release(tag)
            release.upload_asset(path=data_file, label=path.split(data_file)[1], content_type="application/gzip")

        # --- Memo ---
        # release.target_commitish  # 'master'
        # release.tag_name    # '0.5.0'
        # release.title       # 'First public release'
        # release.body        # markdown body
        # release.draft       # False
        # release.prerelease  # False
        # #
        # release.author
        # release.created_at  # datetime.datetime(2018, 11, 9, 17, 49, 56)
        # release.published_at  # datetime.datetime(2018, 11, 9, 20, 11, 10)
        # release.last_modified  # None
        # #
        # release.id           # 13928525
        # release.etag         # 'W/"dfab7a13086d1b44fe290d5d04125124"'
        # release.url          # 'https://api.github.com/repos/smarie/python-pytest-harvest/releases/13928525'
        # release.html_url     # 'https://github.com/smarie/python-pytest-harvest/releases/tag/0.5.0'
        # release.tarball_url  # 'https://api.github.com/repos/smarie/python-pytest-harvest/tarball/0.5.0'
        # release.zipball_url  # 'https://api.github.com/repos/smarie/python-pytest-harvest/zipball/0.5.0'
        # release.upload_url   # 'https://uploads.github.com/repos/smarie/python-pytest-harvest/releases/13928525/assets{?name,label}'


if __name__ == '__main__':
    create_or_update_release()
