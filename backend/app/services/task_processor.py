"""
Task Processor Service
Background worker that processes pending tasks and executes them on devices.
"""
import asyncio
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models.task import Task, TaskStatus, TaskType
from ..models.device import Device, DeviceStatus
from .config_executor import config_executor, ConfigExecutorError

logger = logging.getLogger(__name__)


class TaskProcessor:
    """
    Background task processor.
    Polls for pending tasks and executes them on devices.
    """

    def __init__(self, poll_interval: int = 10):
        """
        Initialize task processor.

        Args:
            poll_interval: Seconds between polling for new tasks
        """
        self.poll_interval = poll_interval
        self.running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the task processor"""
        if self.running:
            logger.warning("Task processor already running")
            return

        self.running = True
        self._task = asyncio.create_task(self._process_loop())
        logger.info("Task processor started")

    async def stop(self):
        """Stop the task processor"""
        if not self.running:
            return

        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Task processor stopped")

    async def _process_loop(self):
        """Main processing loop"""
        while self.running:
            try:
                await self._process_pending_tasks()
            except Exception as e:
                logger.error(f"Error in task processing loop: {str(e)}", exc_info=True)

            # Wait before next poll
            await asyncio.sleep(self.poll_interval)

    async def _process_pending_tasks(self):
        """Process all pending tasks"""
        db = SessionLocal()
        try:
            # Get pending tasks
            pending_tasks = db.query(Task).filter(
                Task.status == TaskStatus.PENDING
            ).order_by(Task.created_at).all()

            if not pending_tasks:
                return

            logger.info(f"Found {len(pending_tasks)} pending tasks")

            for task in pending_tasks:
                try:
                    await self._process_task(task, db)
                except Exception as e:
                    logger.error(f"Failed to process task {task.id}: {str(e)}", exc_info=True)

            db.commit()

        finally:
            db.close()

    async def _process_task(self, task: Task, db: Session):
        """
        Process a single task.

        Args:
            task: Task object
            db: Database session
        """
        logger.info(f"Processing task {task.id} (type: {task.task_type}) for device {task.device_id}")

        # Get device
        device = db.query(Device).filter(Device.id == task.device_id).first()
        if not device:
            task.status = TaskStatus.FAILED
            task.error_message = f"Device {task.device_id} not found"
            task.completed_at = datetime.utcnow()
            logger.error(f"Task {task.id}: Device not found")
            return

        # Mark task as in progress
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        db.commit()

        try:
            # Execute based on task type
            if task.task_type == TaskType.CONFIG_UPDATE:
                result = await self._execute_config_update(device, task)

            elif task.task_type == TaskType.STATUS_COLLECTION:
                result = await self._execute_status_collection(device, task)

            elif task.task_type == TaskType.COMMAND_EXECUTION:
                result = await self._execute_command(device, task)

            elif task.task_type == TaskType.FIRMWARE_UPDATE:
                result = await self._execute_firmware_update(device, task)

            else:
                raise ValueError(f"Unknown task type: {task.task_type}")

            # Update task with result
            task.result = result
            task.status = TaskStatus.COMPLETED if result.get("success") else TaskStatus.FAILED
            task.completed_at = datetime.utcnow()

            if not result.get("success"):
                task.error_message = result.get("error", "Task execution failed")

            logger.info(f"Task {task.id} completed: {task.status}")

        except Exception as e:
            # Handle task failure
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()

            # Check if we should retry
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.started_at = None
                task.completed_at = None
                logger.warning(f"Task {task.id} failed, will retry ({task.retry_count}/{task.max_retries})")
            else:
                logger.error(f"Task {task.id} failed permanently after {task.retry_count} retries")

    async def _execute_config_update(
        self,
        device: Device,
        task: Task
    ) -> dict:
        """Execute configuration update task"""
        config = task.payload.get("config")
        if not config:
            return {
                "success": False,
                "error": "No configuration provided in task payload"
            }

        try:
            result = await config_executor.execute_config(device, config)

            # Update device configuration if successful
            if result.get("success"):
                device.current_config = config
                device.last_config_update = datetime.utcnow()
                device.status = DeviceStatus.ONLINE

            return result

        except ConfigExecutorError as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _execute_status_collection(
        self,
        device: Device,
        task: Task
    ) -> dict:
        """Execute status collection task"""
        try:
            status = await config_executor.get_device_status(device)

            # Update device metadata with status
            if not device.metadata:
                device.metadata = {}

            device.metadata["last_status"] = status
            device.metadata["last_status_collection"] = datetime.utcnow().isoformat()
            device.last_check_in = datetime.utcnow()

            # Update device status based on collection success
            if status.get("status") != "error":
                device.status = DeviceStatus.ONLINE
            else:
                device.status = DeviceStatus.ERROR

            return {
                "success": True,
                "status": status
            }

        except Exception as e:
            device.status = DeviceStatus.ERROR
            return {
                "success": False,
                "error": str(e)
            }

    async def _execute_command(
        self,
        device: Device,
        task: Task
    ) -> dict:
        """Execute raw command task"""
        commands = task.payload.get("commands", [])
        if not commands:
            return {
                "success": False,
                "error": "No commands provided in task payload"
            }

        try:
            from .ssh_manager import ssh_manager

            if device.vendor.value == "ubiquiti":
                return {
                    "success": False,
                    "error": "Command execution not supported for UniFi devices"
                }

            outputs = await ssh_manager.execute_commands(
                host=device.ip_address,
                username=device.ssh_username,
                password=device.ssh_password,
                key_path=device.ssh_key,
                commands=commands,
                port=device.ssh_port or 22,
                timeout=60
            )

            return {
                "success": True,
                "commands": commands,
                "outputs": outputs
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _execute_firmware_update(
        self,
        device: Device,
        task: Task
    ) -> dict:
        """Execute firmware update task"""
        # TODO: Implement firmware update logic
        # This is vendor-specific and complex
        logger.warning(f"Firmware update not yet implemented for task {task.id}")

        return {
            "success": False,
            "error": "Firmware update not yet implemented"
        }

    async def process_task_now(self, task_id: int) -> dict:
        """
        Process a specific task immediately (for testing/manual execution).

        Args:
            task_id: Task ID to process

        Returns:
            Processing result
        """
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found"
                }

            await self._process_task(task, db)
            db.commit()

            return {
                "success": True,
                "task_id": task_id,
                "status": task.status.value
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()


# Global task processor instance
task_processor = TaskProcessor()
