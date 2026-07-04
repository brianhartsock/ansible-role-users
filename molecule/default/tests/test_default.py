"""testinfra tests for the molecule verify stage"""

from passlib.context import CryptContext


def test_user_exists(host):
    """Verify the test user was created."""
    user = host.user('testuser')
    assert user.exists
    assert user.group == 'testgroup'
    assert 'sudo' in user.groups


def test_user_home(host):
    """Verify home directory permissions."""
    home = host.file('/home/testuser')
    assert home.exists
    assert home.is_directory
    assert home.mode == 0o750


def test_ssh_directory(host):
    """Verify .ssh directory exists with correct permissions."""
    ssh_dir = host.file('/home/testuser/.ssh')
    assert ssh_dir.exists
    assert ssh_dir.is_directory
    assert ssh_dir.mode == 0o700


def test_authorized_keys(host):
    """Verify authorized_keys file contains the test key."""
    auth_keys = host.file('/home/testuser/.ssh/authorized_keys')
    assert auth_keys.exists
    assert auth_keys.contains('testuser@molecule')


def test_ssh_key_generated(host):
    """Verify SSH key pair was generated."""
    key = host.file('/home/testuser/.ssh/id_ed25519')
    assert key.exists
    assert key.mode == 0o600


def test_primary_group_gid(host):
    """Verify the primary group was created with the specified GID."""
    group = host.group('testgroup')
    assert group.exists
    assert group.gid == 1050


def test_secondary_group_gid(host):
    """Verify secondary groups were created with specified GIDs."""
    group = host.group('testgroup2')
    assert group.exists
    assert group.gid == 1051


def test_giduser_inherits_role_defaults(host):
    """Verify a user with no overrides gets role-level groups."""
    user = host.user('giduser')
    assert user.exists
    assert user.group == 'testgroup'
    assert 'testgroup2' in user.groups


def test_default_group_matches_username(host):
    """Verify group defaults to username when users_group unset."""
    user = host.user('defaultuser')
    assert user.exists
    assert user.group == 'defaultuser'


def test_update1(host):
    """Verify testuser_update1 has home update1a (overwritten)"""
    user = host.user('testuser_update1')
    assert user.exists
    assert user.home == '/home/update1a'


def test_update2(host):
    """Verify testuser_update2 has home update2 (not overwritten)"""
    user = host.user('testuser_update2')
    assert user.exists
    assert user.home == '/home/update2'


def test_randomuser_exists(host):
    """Verify the random_password test user was created."""
    user = host.user('randomuser')
    assert user.exists


def test_randomuser_password_file(host):
    """
    Verify that the correct password is written to file
    """
    user = host.user("randomuser")
    pw_file = host.file(f"{user.home}/password")

    assert pw_file.exists
    assert pw_file.is_file

    # basic hygiene checks
    assert pw_file.user == "randomuser"
    assert pw_file.mode == 0o600

    password = pw_file.content_string.strip()
    assert password != ""

    shadow_lines = host.file("/etc/shadow").content_string
    line = next(
            thisline for thisline in shadow_lines.splitlines()
            if thisline.startswith(f"{user.name}:")
            )

    shadow_hash = line.split(":")[1]
    assert shadow_hash, "shadow entry for randomuser not found"

    pwd_ctx = CryptContext(
        schemes=["sha512_crypt", "bcrypt", "md5_crypt"],
        deprecated="auto",
    )

    # verify against whatever hash algorithm the system uses
    assert pwd_ctx.verify(password, shadow_hash)
