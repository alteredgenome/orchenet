#!/usr/bin/env python3
"""
OrcheNet Agent - Device-side agent for phone-home architecture
Runs on managed network devices to check in with the server and execute tasks.
"""
import argparse
import json
import logging
import os
import sys
import time
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import requests
    import yaml
except ImportError:
    print("Error: Required packages not installed. Run: pip install requests pyyaml")
    sys.exit(1)


class OrcheNetAgent:
    """Agent that runs on network devices to communicate with OrcheNet server"""

    def __init__(self, config_path: str):
        """
        Initialize agent with configuration

        Args:
            config_path: Path to agent configuration file
        """
        self.config = self._load_config(config_path)
        self.server_url = self.config.get("server_url")
        self.device_id = self.config.get("device_id")
        self.check_in_interval = self.config.get("check_in_interval", 60)
        self.api_key = self.config.get("api_key")

        # Setup logging
        log_level = self.config.get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("OrcheNetAgent")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load agent configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config from {config_path}: {e}")
            sys.exit(1)

    def check_in(self) -> Optional[Dict[str, Any]]:
        """
        Check in with server to retrieve pending tasks

        Returns:
            Dictionary of pending tasks or None if check-in failed
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(
                f"{self.server_url}/api/agent/checkin",
                json={
                    "device_id": self.device_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": self._collect_status()
                },
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                self.logger.info("Check-in successful")
                return response.json()
            else:
                self.logger.error(f"Check-in failed: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Check-in error: {e}")
            return None

    def _collect_status(self) -> Dict[str, Any]:
        """
        Collect device status information

        Returns:
            Dictionary containing device status
        """
        # TODO: Implement vendor-specific status collection
        return {
            "uptime": 0,
            "cpu_usage": 0,
            "memory_usage": 0,
            "timestamp": datetime.utcnow().isoformat()
        }

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task received from server

        Args:
            task: Task dictionary from server

        Returns:
            Task result dictionary
        """
        task_id = task.get("id")
        task_type = task.get("type")

        self.logger.info(f"Executing task {task_id}: {task_type}")

        try:
            if task_type == "config_update":
                return self._execute_config_update(task)
            elif task_type == "command_execution":
                return self._execute_command(task)
            elif task_type == "status_collection":
                return self._execute_status_collection(task)
            else:
                return {
                    "success": False,
                    "error": f"Unknown task type: {task_type}"
                }

        except Exception as e:
            self.logger.error(f"Task execution error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_config_update(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute configuration update task"""
        # TODO: Implement config update logic
        self.logger.info("Config update task - not yet implemented")
        return {"success": True, "message": "Config update placeholder"}

    def _execute_command(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command task"""
        # TODO: Implement command execution logic
        self.logger.info("Command execution task - not yet implemented")
        return {"success": True, "message": "Command execution placeholder"}

    def _execute_status_collection(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute status collection task"""
        status = self._collect_status()
        return {"success": True, "status": status}

    def report_result(self, task_id: int, result: Dict[str, Any]) -> bool:
        """
        Report task execution result back to server

        Args:
            task_id: ID of completed task
            result: Task result dictionary

        Returns:
            True if report was successful
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(
                f"{self.server_url}/api/agent/task/{task_id}/result",
                json=result,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                self.logger.info(f"Result reported for task {task_id}")
                return True
            else:
                self.logger.error(f"Result report failed: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Result report error: {e}")
            return False

    def run(self):
        """Main agent loop - check in periodically and execute tasks"""
        self.logger.info(f"Starting OrcheNet Agent for device {self.device_id}")
        self.logger.info(f"Server: {self.server_url}")
        self.logger.info(f"Check-in interval: {self.check_in_interval}s")

        while True:
            try:
                # Check in with server
                response = self.check_in()

                if response and "tasks" in response:
                    tasks = response["tasks"]
                    self.logger.info(f"Received {len(tasks)} task(s)")

                    # Execute each task
                    for task in tasks:
                        result = self.execute_task(task)
                        self.report_result(task["id"], result)

                # Wait before next check-in
                time.sleep(self.check_in_interval)

            except KeyboardInterrupt:
                self.logger.info("Agent stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                time.sleep(self.check_in_interval)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OrcheNet Device Agent")
    parser.add_argument(
        "--config",
        default="/etc/orchenet/agent.yaml",
        help="Path to agent configuration file"
    )
    args = parser.parse_args()

    agent = OrcheNetAgent(args.config)
    agent.run()


if __name__ == "__main__":
    main()
