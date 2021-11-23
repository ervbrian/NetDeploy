from netmiko import ConnectHandler
from typing import List


class ConfigurationError(Exception):
    "Raised when errors present in config push output"


def run_show_command(
    host: str, key_file: str, command: str, port: int, user: str, use_keys: bool
) -> str:

    dev_connect = {
        "device_type": "autodetect",
        "host": host,
        "port": port,
        "username": user,
        "use_keys": use_keys,
        "key_file": key_file,
    }

    net_connect = ConnectHandler(**dev_connect)
    output = net_connect.send_command(command, use_textfsm=False)
    net_connect.disconnect()

    return output


def run_validation(
    host: str,
    key_file: str,
    command: str,
    expected_output: str,
    exact_match: bool,
    port: int,
    user: str,
    use_keys: bool,
    retry: int = 1,
) -> bool:
    attempt = 1
    while attempt <= retry:
        print(
            f"\n## Validation attempt {attempt}/{retry} ##\n  host: {host}\n  command: {command}\n  expected output: {expected_output}\n"
        )
        output = run_show_command(host, key_file, command, port, user, use_keys)
        if exact_match:
            if output == expected_output:
                print("VALIDATION SUCCESSFUL\n")
                return True
        else:
            if expected_output in output:
                return True
        print("VALIDATION FAILED\n")
        attempt += 1
    return False


def push_configs(
    host: str, key_file: str, configs: List[str], port: int, user: str, use_keys: bool
) -> str:

    print(f"Pushing configurations to {host}")

    dev_connect = {
        "device_type": "cisco_ios",
        "host": host,
        "port": port,
        "username": user,
        "use_keys": use_keys,
        "key_file": key_file,
    }

    net_connect = ConnectHandler(**dev_connect)
    output = net_connect.send_config_set(configs)
    net_connect.disconnect()

    # error messages start with '%'
    try:
        assert "\n%" not in output
    except AssertionError as e:
        print(f"ERROR pushing configurations. Please check output: \n{output}")
        raise ConfigurationError

    return output
