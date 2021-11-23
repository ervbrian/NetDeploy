<p align="center">
  <a href="https://github.com/ervbrian/NetDeploy">
    <img src="images/logo.jpeg" alt="Logo" width="320" height="320">
  </a>

  <h3 align="center">NetDeploy</h3>

  <p align="center">
    A configuration deployment and validation tool for network devices
    <br />
    <a href="https://github.com/ervbrian/NetDeploy/blob/master/README.md"><strong>Explore the docs »</strong></a>
    <br />
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

### Problem Statement
Network deployments typically consist of a series of validation and configuration steps across one or more devices. Manually typing configurations can lead to unintended errors or typos. Additionally, interpreting large amounts of "show command" output under pressure can lead to misinterpretation of environment health and/or state. 

### Solution
NetDeploy allows network engineers to focus on the deployment steps and validation up-front, reducing the amount of information that needs to be interpreted during deployments. NetDeploy parses deployment steps specified in an input YAML, ensures the checks pass, pushes configuration changes and automatically rolls when validation steps fail. 

### Built With

* [Python](https://www.python.org/)
* [netmiko](https://pypi.org/project/netmiko/)


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* Python3 is required to install a virtual environment for NetDeploy

### Installation

1. Clone the repo
   ```sh
   $ git clone https://github.com/ervbrian/NetDeploy.git
   ```
2. Create Virtual Environment
   ```sh
   cd NetDeploy
   $ python3 -m venv .venv
   ```
3. Activate Virtual Environment
   ```sh
   $ source .venv/bin/activate
   ```
4. Install Python Requirements
   ```sh
   $ python3 -m pip install -r requirements.txt
   ```

<!-- USAGE EXAMPLES -->
## Usage

### Creating deployment YAML
A deployment YAML outlines the validation and configuration steps required to achieve a certain outcome on your network. 

#### Example
```yaml
---
  deployment: 
    steps:
      step_01: 
          type: validation                                              # Required. Options: [configuration, validation]
          name: "Verify OSPF is not configured"                         # Required. Provides a brief description of step
          devices: ["18.236.182.196"]                                   # Required. List of device names or IPs
          command: "show ip proto | count ospf"                         # Required. Command that will be executed on device(s)
          expected_output: "Number of lines which match regexp = 1"     # Required. Expected outout from "command" output
          exact_match: True                                             # Required. Specifies whether "command" output must be the ONLY output received. Options: [True, False]
          retry: 1                                                      # Required. Number of retry attempts allowed for step
      step_02:
          type: configuration
          name: "Push OSPF configs"
          devices: ["18.236.182.196"]
          config: "examples/ospf_config.txt"                            # Required. Path to configuration file that will be applied to device(s)
          rollback_config: "examples/ospf_config_rollback.txt"          # Required. Path to rollback configuration. This MUST return device configs to pre-deployment state.
      step_03:
          type: validation
          name: "Verify OSPF is configured"
          devices: ["18.236.182.196"]
          command: "show ip proto | count ospf"
          expected_output: "Number of lines which match regexp = 1"
          exact_match: True
          retry: 1
      step_04:
          type: validation
          name: "Verify all loopbacks are OSPF enabled"
          devices: ["18.236.182.196"]
          command: "show ip ospf int | count ^Loopback"
          expected_output: "Number of lines which match regexp = 11"
          exact_match: True
          retry: 1
```

### Example Executions

#### Successful Deployment 
```
(.venv) ➜  NetDeploy python deploy.py -i examples/stage_ospf.yaml -u ec2-user -sk ~/.ssh/ervbrian_key_pair.pem
Processed 4 deployment steps

Deployment Summary:
  step_01: Verify OSPF is not configured
    Devices: ['18.236.182.196']

  step_02: Push OSPF configs
    Devices: ['18.236.182.196']

  step_03: Verify OSPF is configured
    Devices: ['18.236.182.196']

  step_04: Verify all loopbacks are OSPF enabled
    Devices: ['18.236.182.196']


## Validation attempt 1/1 ##
  host: 18.236.182.196
  command: show ip proto | count ospf
  expected output: Number of lines which match regexp = 0

VALIDATION SUCCESSFUL

Pushing configurations to 18.236.182.196

## Validation attempt 1/1 ##
  host: 18.236.182.196
  command: show ip proto | count ospf
  expected output: Number of lines which match regexp = 1

VALIDATION SUCCESSFUL


## Validation attempt 1/1 ##
  host: 18.236.182.196
  command: show ip ospf int | count ^Loopback
  expected output: Number of lines which match regexp = 11

VALIDATION SUCCESSFUL


## DEPLOYMENT STATUS: COMPLETE ##
```

#### Failed deployment with rollback
Example deployment where a validation step failed after config push, resulting in auto-rollback.
```
(.venv) ➜  NetDeploy python deploy.py -i examples/stage_ospf.yaml -u ec2-user -sk ~/.ssh/ervbrian_key_pair.pem
Processed 4 deployment steps

Deployment Summary:
  step_01: Verify OSPF is not configured
    Devices: ['18.236.182.196']

  step_02: Push OSPF configs
    Devices: ['18.236.182.196']

  step_03: Verify OSPF is configured
    Devices: ['18.236.182.196']

  step_04: Verify all loopbacks are OSPF enabled
    Devices: ['18.236.182.196']


## Validation attempt 1/1 ##
  host: 18.236.182.196
  command: show ip proto | count ospf
  expected output: Number of lines which match regexp = 1

VALIDATION SUCCESSFUL

Pushing configurations to 18.236.182.196

## Validation attempt 1/1 ##
  host: 18.236.182.196
  command: show ip proto | count ospf
  expected output: Number of lines which match regexp = 1

VALIDATION SUCCESSFUL


## Validation attempt 1/1 ##
  host: 18.236.182.196
  command: show ip ospf int | count ^Loopback
  expected output: Number of lines which match regexp = 10

VALIDATION FAILED

ENTERING ROLLBACK MODE

## Validation attempt 1/1 ##
  host: 18.236.182.196
  command: show ip proto | count ospf
  expected output: Number of lines which match regexp = 1

VALIDATION SUCCESSFUL

Pushing configurations to 18.236.182.196

## Validation attempt 1/1 ##
  host: 18.236.182.196
  command: show ip proto | count ospf
  expected output: Number of lines which match regexp = 1

VALIDATION FAILED


## DEPLOYMENT STATUS: FAILED ##
```

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact

Brian Ervin - brian.s.ervin@gmail.com

Project Link: [https://github.com/ervbrian/NetDeploy](https://github.com/ervbrian/NetDeploy)
