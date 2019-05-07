import pytest

from bigbus import UserInt

@pytest.mark.parametrize('command', ['Sell', 'Issue Refund', 'Report', 'Quit'])
def test_is_valid_command(command):
    userint = UserInt()
    assert userint.is_valid_command(command)
