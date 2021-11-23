import yaml

from utils.device_connect import push_configs, run_validation


def parse_deployment(filename: str) -> dict:
    with open(filename, "r") as f:
        deployment = yaml.load(f, Loader=yaml.Loader)

    steps = len(deployment["deployment"]["steps"])
    print(f"Processed {steps} deployment steps")

    return deployment


class Deployment:
    def __init__(self, input_yaml: str, user: str, ssh_key: str) -> None:
        self.parameters = parse_deployment(filename=input_yaml)
        self.steps = self.parameters["deployment"]["steps"]
        self.user = user
        self.ssh_key = ssh_key
        self.status = "ACTIVE"
        self.current_step = 0
        self.direction = "forward"

    def _step_processing_valid(self) -> bool:
        status_active = self.status == "ACTIVE"
        not_at_end = self.current_step < len(self.steps)
        not_at_beginning = self.current_step >= 0

        if status_active and not_at_end and not_at_beginning:
            return True
        return False

    def _increment_step(self) -> None:
        if self.direction == "forward":
            self.current_step += 1
        elif self.direction == "rollback":
            self.current_step -= 1

    def _deployment_status(self) -> None:
        if self.direction == "forward":
            self.status = "COMPLETE"
        else:
            self.status = "FAILED"

        print(f"\n## DEPLOYMENT STATUS: {self.status} ## \n")

    def _process_validations(self, step_key: str) -> None:
        for device in self.steps[step_key]["devices"]:
            validation = run_validation(
                host=device,
                user=self.user,
                key_file=self.ssh_key,
                command=self.steps[step_key]["command"],
                expected_output=self.steps[step_key]["expected_output"],
                exact_match=self.steps[step_key]["exact_match"],
                retry=self.steps[step_key]["retry"],
                port=22,
                use_keys=True,
            )
            if not validation and self.direction != "rollback":
                print(f"ENTERING ROLLBACK MODE")
                self.direction = "rollback"  # FIX issue with reassigning enum

    def _process_config_push(self, step_key: str) -> None:
        config_path = (
            self.steps[step_key]["config"]
            if self.direction == "forward"
            else self.steps[step_key]["rollback_config"]
        )
        for device in self.steps[step_key]["devices"]:
            push_configs(
                host=device,
                user=self.user,
                key_file=self.ssh_key,
                configs=open(config_path, "r").readlines(),
                port=22,
                use_keys=True,
            )

    def display_summary(self) -> None:
        print(f"\nDeployment Summary:")

        for step in self.steps:
            print(f"  {step}: {self.steps[step]['name']}")
            print(f"    Devices: {self.steps[step]['devices']}\n")

    def execute(self) -> None:
        while self._step_processing_valid():
            step_key = list(self.steps.keys())[self.current_step]

            if self.steps[step_key]["type"] == "validation":
                self._process_validations(step_key)

            elif self.steps[step_key]["type"] == "configuration":
                self._process_config_push(step_key)

            self._increment_step()

        self._deployment_status()
