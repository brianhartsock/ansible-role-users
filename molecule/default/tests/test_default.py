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
