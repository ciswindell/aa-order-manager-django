"""Basecamp API Service.

Provides high-level interface for Basecamp 3 API operations.
"""

import logging
import re
import time
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

BASECAMP_API_BASE = "https://3.basecampapi.com"
USER_AGENT = "aa-order-manager (support@example.com)"


class BasecampService:
    """High-level wrapper for Basecamp 3 API operations."""

    def __init__(self, access_token: str):
        """Initialize service with access token.

        Args:
            access_token: OAuth access token for API calls
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": USER_AGENT,
        }

    # ============================================================================
    # Validation Helpers (T001-T004)
    # ============================================================================

    def _validate_id(self, value: Any, param_name: str) -> None:
        """Validate ID parameter is non-empty numeric string.

        Args:
            value: Value to validate
            param_name: Name of parameter for error message

        Raises:
            ValueError: If value is not a valid numeric string
        """
        if not value or not str(value).strip():
            raise ValueError(f"Invalid {param_name}: must not be empty")

        # Allow both int and string representations of numbers
        str_value = str(value).strip()
        if not str_value.isdigit():
            raise ValueError(f"Invalid {param_name}: must be numeric string")

    def _validate_name(self, value: str, max_length: int = 255) -> None:
        """Validate name is non-empty and within length limit.

        Args:
            value: Name to validate
            max_length: Maximum allowed length (default: 255)

        Raises:
            ValueError: If name is empty or exceeds max length
        """
        if not value or not value.strip():
            raise ValueError("Name required and must not be empty")

        if len(value) > max_length:
            raise ValueError(
                f"Name must be ≤{max_length} characters (got {len(value)})"
            )

    def _validate_description(self, value: Optional[str]) -> None:
        """Validate description length.

        Args:
            value: Description to validate (can be None)

        Raises:
            ValueError: If description exceeds max length
        """
        if value is not None and len(value) > 10000:
            raise ValueError(
                f"Description must be ≤10,000 characters (got {len(value)})"
            )

    def _validate_date_format(self, value: Optional[str]) -> None:
        """Validate date is in YYYY-MM-DD format.

        Args:
            value: Date string to validate (can be None)

        Raises:
            ValueError: If date format is invalid
        """
        if value is None:
            return

        # Check format with regex
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            raise ValueError(f"Invalid date format: must be YYYY-MM-DD (got '{value}')")

    # ============================================================================
    # Error Handling (T005)
    # ============================================================================

    def _handle_api_error(
        self, response: requests.Response, context: dict, max_retries: int = 3
    ) -> Optional[dict]:
        """Handle API error responses with exponential backoff for rate limits.

        Args:
            response: HTTP response object
            context: Context dict with account_id, endpoint, etc. for logging
            max_retries: Maximum retry attempts for 429 errors

        Returns:
            dict: Response JSON if retry succeeded, None otherwise

        Raises:
            requests.exceptions.HTTPError: For non-retryable errors (4xx/5xx)
        """
        status_code = response.status_code

        # Success - no error handling needed
        if 200 <= status_code < 300:
            return response.json()

        # Rate limit (429) - retry with exponential backoff
        if status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))

            for attempt in range(max_retries):
                wait_time = retry_after * (2**attempt)  # Exponential backoff

                logger.warning(
                    f"Basecamp API rate limit | "
                    f"account_id={context.get('account_id')} | "
                    f"endpoint={context.get('endpoint')} | "
                    f"attempt={attempt + 1}/{max_retries} | "
                    f"waiting={wait_time}s"
                )

                time.sleep(wait_time)

                # Retry the request (caller should handle this)
                return None  # Signal caller to retry

            # Max retries exceeded
            logger.error(
                f"Basecamp API rate limit exceeded | "
                f"account_id={context.get('account_id')} | "
                f"endpoint={context.get('endpoint')} | "
                f"max_retries={max_retries}"
            )
            response.raise_for_status()

        # Token expiration (401) - caller should refresh token
        if status_code == 401:
            logger.warning(
                f"Basecamp API unauthorized | "
                f"account_id={context.get('account_id')} | "
                f"endpoint={context.get('endpoint')} | "
                f"hint=token_may_be_expired"
            )
            response.raise_for_status()

        # Other client errors (4xx) - don't retry
        if 400 <= status_code < 500:
            error_msg = response.text
            logger.error(
                f"Basecamp API client error | "
                f"status={status_code} | "
                f"account_id={context.get('account_id')} | "
                f"endpoint={context.get('endpoint')} | "
                f"error={error_msg[:200]}"
            )
            response.raise_for_status()

        # Server errors (5xx) - retry once
        if status_code >= 500:
            logger.warning(
                f"Basecamp API server error | "
                f"status={status_code} | "
                f"account_id={context.get('account_id')} | "
                f"endpoint={context.get('endpoint')} | "
                f"retrying=true"
            )
            # Signal caller to retry once
            return None

        # Unknown error
        response.raise_for_status()
        return None

    # ============================================================================
    # Logging Helper (T006)
    # ============================================================================

    def _log_api_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        context: dict,
        duration_ms: Optional[float] = None,
    ) -> None:
        """Log API request with tiered levels (INFO/WARNING/ERROR).

        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            endpoint: API endpoint path
            status: HTTP status code
            context: Context dict with account_id, request_id, etc.
            duration_ms: Request duration in milliseconds (optional)
        """
        # Build log message
        log_parts = [
            f"Basecamp API {method}",
            f"endpoint={endpoint}",
            f"status={status}",
        ]

        # Add context fields
        if context.get("account_id"):
            log_parts.append(f"account_id={context['account_id']}")

        if context.get("request_id"):
            log_parts.append(f"request_id={context['request_id']}")

        if duration_ms is not None:
            log_parts.append(f"duration_ms={duration_ms:.0f}")

        log_message = " | ".join(log_parts)

        # Tiered logging based on status code
        if 200 <= status < 300:
            # Success - INFO level
            logger.info(log_message)
        elif status == 429:
            # Rate limit - WARNING level (handled by retry logic)
            logger.warning(f"{log_message} | rate_limit=true")
        elif 400 <= status < 500:
            # Client error - ERROR level
            logger.error(f"{log_message} | error=client_error")
        elif status >= 500:
            # Server error - ERROR level
            logger.error(f"{log_message} | error=server_error")
        else:
            # Unknown status - WARNING level
            logger.warning(f"{log_message} | unknown_status=true")

    # ============================================================================
    # Project Methods (T007-T012) - User Story 1
    # ============================================================================

    def list_projects(self, account_id: str) -> list[dict]:
        """Get all projects for a Basecamp account.

        Args:
            account_id: Basecamp account ID

        Returns:
            list: List of project objects with id, name, description, status, dock

        Raises:
            ValueError: If account_id is invalid
            requests.exceptions.HTTPError: If API call fails (401, 429, etc.)
        """
        # T010: Input validation
        self._validate_id(account_id, "account_id")

        # Build endpoint
        endpoint = f"/{account_id}/projects.json"
        url = f"{BASECAMP_API_BASE}{endpoint}"

        # T012: Log request start
        context = {"account_id": account_id, "endpoint": endpoint}
        start_time = time.time()

        try:
            # Make API request with timeout
            response = requests.get(url, headers=self.headers, timeout=10)

            # T011: Error handling
            if response.status_code != 200:
                self._handle_api_error(response, context)

            # Success - get response data
            duration_ms = (time.time() - start_time) * 1000
            self._log_api_request(
                "GET", endpoint, response.status_code, context, duration_ms
            )

            return response.json()

        except requests.exceptions.Timeout:
            logger.error(
                f"Basecamp API timeout | "
                f"account_id={account_id} | "
                f"endpoint={endpoint} | "
                f"timeout=10s"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Basecamp API request failed | "
                f"account_id={account_id} | "
                f"endpoint={endpoint} | "
                f"error={str(e)}"
            )
            raise

    def get_project(self, account_id: str, project_id: str) -> dict:
        """Get specific project details by ID.

        Args:
            account_id: Basecamp account ID
            project_id: Project ID to retrieve

        Returns:
            dict: Project object with id, name, description, status, dock

        Raises:
            ValueError: If account_id or project_id is invalid
            requests.exceptions.HTTPError: If API call fails (401, 404, 429, etc.)
        """
        # T010: Input validation
        self._validate_id(account_id, "account_id")
        self._validate_id(project_id, "project_id")

        # Build endpoint
        endpoint = f"/{account_id}/projects/{project_id}.json"
        url = f"{BASECAMP_API_BASE}{endpoint}"

        # T012: Log request start
        context = {
            "account_id": account_id,
            "project_id": project_id,
            "endpoint": endpoint,
        }
        start_time = time.time()

        try:
            # Make API request with timeout
            response = requests.get(url, headers=self.headers, timeout=10)

            # T011: Error handling
            if response.status_code != 200:
                self._handle_api_error(response, context)

            # Success - get response data
            duration_ms = (time.time() - start_time) * 1000
            self._log_api_request(
                "GET", endpoint, response.status_code, context, duration_ms
            )

            return response.json()

        except requests.exceptions.Timeout:
            logger.error(
                f"Basecamp API timeout | "
                f"account_id={account_id} | "
                f"project_id={project_id} | "
                f"endpoint={endpoint} | "
                f"timeout=10s"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Basecamp API request failed | "
                f"account_id={account_id} | "
                f"project_id={project_id} | "
                f"endpoint={endpoint} | "
                f"error={str(e)}"
            )
            raise

    def _get_todoset_id(self, account_id: str, project_id: str) -> str:
        """Extract todoset ID from project's dock.

        Every Basecamp project has one todoset that contains all to-do lists.
        This helper extracts the todoset ID from the project's dock array.

        Args:
            account_id: Basecamp account ID
            project_id: Project ID

        Returns:
            str: Todoset ID

        Raises:
            ValueError: If project has no todoset or invalid IDs
            requests.exceptions.HTTPError: If API call fails
        """
        # Get project details
        project = self.get_project(account_id, project_id)

        # Extract todoset from dock
        dock = project.get("dock", [])
        todoset = next((item for item in dock if item.get("name") == "todoset"), None)

        if not todoset:
            raise ValueError(
                f"Project {project_id} has no todoset in dock. "
                f"To-dos feature may be disabled for this project."
            )

        todoset_id = todoset.get("id")
        if not todoset_id:
            raise ValueError(f"Project {project_id} todoset has no ID")

        return str(todoset_id)

    # ============================================================================
    # To-Do List Methods (T013-T019) - User Story 2
    # ============================================================================

    def list_todolists(self, account_id: str, project_id: str) -> list[dict]:
        """List all to-do lists in a project.

        Args:
            account_id: Basecamp account ID
            project_id: Project ID

        Returns:
            list: List of to-do list objects with id, name, description

        Raises:
            ValueError: If account_id or project_id is invalid
            requests.exceptions.HTTPError: If API call fails (401, 404, 429, etc.)
        """
        # T016: Input validation
        self._validate_id(account_id, "account_id")
        self._validate_id(project_id, "project_id")

        # Get todoset ID from project (required for listing to-do lists)
        todoset_id = self._get_todoset_id(account_id, project_id)

        # Build endpoint
        endpoint = (
            f"/{account_id}/buckets/{project_id}/todosets/{todoset_id}/todolists.json"
        )
        url = f"{BASECAMP_API_BASE}{endpoint}"

        # T019: Log request start
        context = {
            "account_id": account_id,
            "project_id": project_id,
            "todoset_id": todoset_id,
            "endpoint": endpoint,
        }
        start_time = time.time()

        try:
            # Make API request with timeout
            response = requests.get(url, headers=self.headers, timeout=10)

            # T018: Error handling
            if response.status_code != 200:
                self._handle_api_error(response, context)

            # Success - get response data
            duration_ms = (time.time() - start_time) * 1000
            self._log_api_request(
                "GET", endpoint, response.status_code, context, duration_ms
            )

            return response.json()

        except requests.exceptions.Timeout:
            logger.error(
                f"Basecamp API timeout | "
                f"account_id={account_id} | "
                f"project_id={project_id} | "
                f"endpoint={endpoint} | "
                f"timeout=10s"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Basecamp API request failed | "
                f"account_id={account_id} | "
                f"project_id={project_id} | "
                f"endpoint={endpoint} | "
                f"error={str(e)}"
            )
            raise

    def _check_duplicate_todolist(
        self, account_id: str, project_id: str, name: str
    ) -> bool:
        """Check if to-do list with name already exists in project.

        Performs case-sensitive comparison with whitespace normalization.

        Args:
            account_id: Basecamp account ID
            project_id: Project ID
            name: To-do list name to check

        Returns:
            bool: True if duplicate exists, False otherwise

        Raises:
            ValueError: If IDs are invalid
            requests.exceptions.HTTPError: If API call fails
        """
        # Get all to-do lists in project
        todolists = self.list_todolists(account_id, project_id)

        # Normalize name for comparison (strip whitespace, keep case)
        normalized_name = name.strip()

        # Check for exact match (case-sensitive, whitespace-normalized)
        for todolist in todolists:
            existing_name = todolist.get("name", "").strip()
            if existing_name == normalized_name:
                logger.warning(
                    f"Basecamp duplicate to-do list detected | "
                    f"account_id={account_id} | "
                    f"project_id={project_id} | "
                    f"name={normalized_name} | "
                    f"existing_id={todolist.get('id')}"
                )
                return True

        return False

    def create_todolist(
        self, account_id: str, project_id: str, name: str, description: str = ""
    ) -> dict:
        """Create a new to-do list in a project.

        Args:
            account_id: Basecamp account ID
            project_id: Project ID
            name: To-do list name (max 255 characters)
            description: Optional description (max 10,000 characters)

        Returns:
            dict: Created to-do list object with id, name, description, url

        Raises:
            ValueError: If validation fails or duplicate name exists
            requests.exceptions.HTTPError: If API call fails (401, 404, 422, 429, etc.)
        """
        # T016: Input validation
        self._validate_id(account_id, "account_id")
        self._validate_id(project_id, "project_id")
        self._validate_name(name, max_length=255)
        self._validate_description(description)

        # T017: Check for duplicates
        if self._check_duplicate_todolist(account_id, project_id, name):
            raise ValueError(
                f"To-do list with name '{name}' already exists in project {project_id}. "
                f"Please use a different name."
            )

        # Get todoset ID from project
        todoset_id = self._get_todoset_id(account_id, project_id)

        # Build endpoint
        endpoint = (
            f"/{account_id}/buckets/{project_id}/todosets/{todoset_id}/todolists.json"
        )
        url = f"{BASECAMP_API_BASE}{endpoint}"

        # Build request body
        body = {"name": name}
        if description:
            body["description"] = description

        # T019: Log request start
        context = {
            "account_id": account_id,
            "project_id": project_id,
            "todoset_id": todoset_id,
            "todolist_name": name,
            "endpoint": endpoint,
        }
        start_time = time.time()

        try:
            # Make API request with timeout
            response = requests.post(url, headers=self.headers, json=body, timeout=10)

            # T018: Error handling
            if response.status_code != 201:
                self._handle_api_error(response, context)

            # Success - get response data
            duration_ms = (time.time() - start_time) * 1000
            self._log_api_request(
                "POST", endpoint, response.status_code, context, duration_ms
            )

            created_todolist = response.json()
            logger.info(
                f"Basecamp to-do list created | "
                f"account_id={account_id} | "
                f"project_id={project_id} | "
                f"todolist_id={created_todolist.get('id')} | "
                f"name={name}"
            )

            return created_todolist

        except requests.exceptions.Timeout:
            logger.error(
                f"Basecamp API timeout | "
                f"account_id={account_id} | "
                f"project_id={project_id} | "
                f"endpoint={endpoint} | "
                f"timeout=10s"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Basecamp API request failed | "
                f"account_id={account_id} | "
                f"project_id={project_id} | "
                f"endpoint={endpoint} | "
                f"error={str(e)}"
            )
            raise

    # ============================================================================
    # Existing Methods
    # ============================================================================

    def get_authorization_details(self) -> dict:
        """Get user's Basecamp authorization details including accounts.

        Returns:
            dict: Authorization response with accounts array

        Raises:
            Exception: If API call fails
        """
        response = requests.get(
            "https://launchpad.37signals.com/authorization.json",
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    # ============================================================================
    # To-Do (Task) Methods (T020-T024) - User Story 3
    # ============================================================================

    def create_todo(
        self,
        account_id: str,
        project_id: str,
        todolist_id: str,
        content: str,
        description: str = "",
        due_on: Optional[str] = None,
        assignee_ids: Optional[list[int]] = None,
        group_id: Optional[int] = None,
    ) -> dict:
        """Create a new task (to-do) in a to-do list.

        Args:
            account_id: Basecamp account ID
            project_id: Project ID
            todolist_id: To-do list ID
            content: Task name (required, max 255 chars)
            description: Task description (optional, max 10,000 chars)
            due_on: Due date in YYYY-MM-DD format (optional)
            assignee_ids: List of Basecamp user IDs to assign (optional)
            group_id: Group ID to assign task to (optional)

        Returns:
            dict: Created to-do object with id, content, description, etc.

        Raises:
            ValueError: If validation fails
            requests.exceptions.HTTPError: If API call fails
        """
        # T022: Input validation
        self._validate_id(account_id, "account_id")
        self._validate_id(project_id, "project_id")
        self._validate_id(todolist_id, "todolist_id")
        self._validate_name(content, max_length=255)
        self._validate_description(description)
        if due_on is not None:
            self._validate_date_format(due_on)
        if assignee_ids is not None and not isinstance(assignee_ids, list):
            raise ValueError("assignee_ids must be a list of integers")
        if group_id is not None and not isinstance(group_id, int):
            raise ValueError("group_id must be an integer")

        # Build endpoint
        endpoint = (
            f"/{account_id}/buckets/{project_id}/todolists/{todolist_id}/todos.json"
        )
        url = f"{BASECAMP_API_BASE}{endpoint}"

        # Build request body
        body = {"content": content}
        if description:
            body["description"] = description
        if due_on:
            body["due_on"] = due_on
        if assignee_ids:
            body["assignee_ids"] = assignee_ids
        if group_id is not None:
            body["group_id"] = group_id

        # T024: Log request start
        context = {
            "account_id": account_id,
            "project_id": project_id,
            "todolist_id": todolist_id,
            "content": content[:50],
            "endpoint": endpoint,
        }
        start_time = time.time()

        try:
            # Make API request with timeout
            response = requests.post(url, headers=self.headers, json=body, timeout=10)

            # T023: Error handling
            duration_ms = (time.time() - start_time) * 1000
            if response.status_code >= 400:
                result = self._handle_api_error(response, context)
                if result:
                    return result
                response.raise_for_status()

            # T024: Log success
            self._log_api_request(
                "POST", endpoint, response.status_code, context, duration_ms
            )

            return response.json()

        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "Basecamp API request failed | %s | error=%s",
                " | ".join(f"{k}={v}" for k, v in context.items()),
                str(e),
            )
            self._log_api_request("POST", endpoint, 0, context, duration_ms)
            raise

    def update_todo(
        self,
        account_id: str,
        project_id: str,
        todo_id: str,
        **kwargs,
    ) -> dict:
        """Update an existing task (to-do).

        Args:
            account_id: Basecamp account ID
            project_id: Project ID
            todo_id: To-do ID
            **kwargs: Fields to update (content, description, due_on, assignee_ids, group_id)

        Returns:
            dict: Updated to-do object

        Raises:
            ValueError: If validation fails
            requests.exceptions.HTTPError: If API call fails
        """
        # T022: Input validation
        self._validate_id(account_id, "account_id")
        self._validate_id(project_id, "project_id")
        self._validate_id(todo_id, "todo_id")

        # Validate optional fields if provided
        if "content" in kwargs:
            self._validate_name(kwargs["content"], max_length=255)
        if "description" in kwargs:
            self._validate_description(kwargs["description"])
        if "due_on" in kwargs and kwargs["due_on"] is not None:
            self._validate_date_format(kwargs["due_on"])
        if "assignee_ids" in kwargs and kwargs["assignee_ids"] is not None:
            if not isinstance(kwargs["assignee_ids"], list):
                raise ValueError("assignee_ids must be a list of integers")
        if "group_id" in kwargs and kwargs["group_id"] is not None:
            if not isinstance(kwargs["group_id"], int):
                raise ValueError("group_id must be an integer")

        # Build endpoint
        endpoint = f"/{account_id}/buckets/{project_id}/todos/{todo_id}.json"
        url = f"{BASECAMP_API_BASE}{endpoint}"

        # T024: Log request start
        context = {
            "account_id": account_id,
            "project_id": project_id,
            "todo_id": todo_id,
            "fields": list(kwargs.keys()),
            "endpoint": endpoint,
        }
        start_time = time.time()

        try:
            # Make API request with timeout
            response = requests.put(url, headers=self.headers, json=kwargs, timeout=10)

            # T023: Error handling
            duration_ms = (time.time() - start_time) * 1000
            if response.status_code >= 400:
                result = self._handle_api_error(response, context)
                if result:
                    return result
                response.raise_for_status()

            # T024: Log success
            self._log_api_request(
                "PUT", endpoint, response.status_code, context, duration_ms
            )

            return response.json()

        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "Basecamp API request failed | %s | error=%s",
                " | ".join(f"{k}={v}" for k, v in context.items()),
                str(e),
            )
            self._log_api_request("PUT", endpoint, 0, context, duration_ms)
            raise

    # ============================================================================
    # Group Methods (T025-T030) - User Story 4
    # ============================================================================

    def list_groups(
        self, account_id: str, project_id: str, todolist_id: str
    ) -> list[dict]:
        """List all groups in a to-do list.

        Args:
            account_id: Basecamp account ID
            project_id: Project ID
            todolist_id: To-do list ID

        Returns:
            list: List of group objects with id, name, position

        Raises:
            ValueError: If account_id, project_id, or todolist_id is invalid
            requests.exceptions.HTTPError: If API call fails (404, 429, etc.)
        """
        # T027: Input validation
        self._validate_id(account_id, "account_id")
        self._validate_id(project_id, "project_id")
        self._validate_id(todolist_id, "todolist_id")

        # Build endpoint
        endpoint = (
            f"/{account_id}/buckets/{project_id}/todolists/{todolist_id}/groups.json"
        )
        url = f"{BASECAMP_API_BASE}{endpoint}"

        # T029: Log request start
        context = {
            "account_id": account_id,
            "project_id": project_id,
            "todolist_id": todolist_id,
            "endpoint": endpoint,
        }
        start_time = time.time()

        try:
            # Make API request with timeout
            response = requests.get(url, headers=self.headers, timeout=10)

            # T028: Error handling
            duration_ms = (time.time() - start_time) * 1000
            if response.status_code >= 400:
                result = self._handle_api_error(response, context)
                if result:
                    return result
                response.raise_for_status()

            # T029: Log success
            self._log_api_request(
                "GET", endpoint, response.status_code, context, duration_ms
            )

            return response.json()

        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "Basecamp API request failed | %s | error=%s",
                " | ".join(f"{k}={v}" for k, v in context.items()),
                str(e),
            )
            self._log_api_request("GET", endpoint, 0, context, duration_ms)
            raise

    def create_group(
        self, account_id: str, project_id: str, todolist_id: str, name: str
    ) -> dict:
        """Create a new group (section) in a to-do list.

        Args:
            account_id: Basecamp account ID
            project_id: Project ID
            todolist_id: To-do list ID
            name: Group name (required, max 255 chars)

        Returns:
            dict: Created group object with id, name, position

        Raises:
            ValueError: If validation fails
            requests.exceptions.HTTPError: If API call fails (404, 422, 429, etc.)
        """
        # T027: Input validation
        self._validate_id(account_id, "account_id")
        self._validate_id(project_id, "project_id")
        self._validate_id(todolist_id, "todolist_id")
        self._validate_name(name, max_length=255)

        # Build endpoint
        endpoint = (
            f"/{account_id}/buckets/{project_id}/todolists/{todolist_id}/groups.json"
        )
        url = f"{BASECAMP_API_BASE}{endpoint}"

        # Build request body
        body = {"name": name}

        # T029: Log request start
        context = {
            "account_id": account_id,
            "project_id": project_id,
            "todolist_id": todolist_id,
            "name": name[:50],
            "endpoint": endpoint,
        }
        start_time = time.time()

        try:
            # Make API request with timeout
            response = requests.post(url, headers=self.headers, json=body, timeout=10)

            # T028: Error handling
            duration_ms = (time.time() - start_time) * 1000
            if response.status_code >= 400:
                result = self._handle_api_error(response, context)
                if result:
                    return result
                response.raise_for_status()

            # T029: Log success
            self._log_api_request(
                "POST", endpoint, response.status_code, context, duration_ms
            )

            return response.json()

        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "Basecamp API request failed | %s | error=%s",
                " | ".join(f"{k}={v}" for k, v in context.items()),
                str(e),
            )
            self._log_api_request("POST", endpoint, 0, context, duration_ms)
            raise

    def get_account_info(self, account_id: str) -> dict:
        """Get details for a specific Basecamp account.

        Args:
            account_id: Basecamp account ID

        Returns:
            dict: Account information

        Raises:
            Exception: If API call fails
        """
        response = requests.get(
            f"{BASECAMP_API_BASE}/{account_id}.json",
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
