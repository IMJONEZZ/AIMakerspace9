"""
Parallel execution utilities for AI Life Coach.

This module provides utilities for parallel subagent execution
to improve overall system performance.

Features:
- Parallel tool execution
- Concurrent subagent delegation
- Async wrapper utilities
- Batch processing helpers
"""

import asyncio
import concurrent.futures
import functools
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


@dataclass
class ParallelResult:
    """Result from a parallel execution."""

    name: str
    result: Any
    error: Optional[Exception] = None
    execution_time: float = 0.0

    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.error is None


class ParallelExecutor:
    """
    Execute functions in parallel for improved performance.

    Supports both thread-based and process-based parallelism.
    """

    def __init__(self, max_workers: int = 4, use_processes: bool = False):
        """
        Initialize the parallel executor.

        Args:
            max_workers: Maximum number of parallel workers
            use_processes: Use process pool instead of thread pool
        """
        self.max_workers = max_workers
        self.use_processes = use_processes
        self._executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor

    def execute_parallel(
        self, tasks: List[Tuple[Callable, Tuple, Dict]], timeout: Optional[float] = None
    ) -> List[ParallelResult]:
        """
        Execute multiple tasks in parallel.

        Args:
            tasks: List of (function, args, kwargs) tuples
            timeout: Optional timeout in seconds

        Returns:
            List of ParallelResult objects

        Example:
            >>> executor = ParallelExecutor(max_workers=4)
            >>> tasks = [
            ...     (func1, (arg1,), {}),
            ...     (func2, (arg2,), {'key': 'value'}),
            ... ]
            >>> results = executor.execute_parallel(tasks)
        """
        results = []

        with self._executor_class(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {}
            for name, (func, args, kwargs) in enumerate(tasks):
                start_time = time.perf_counter()
                future = executor.submit(func, *args, **kwargs)
                future_to_task[future] = (
                    name,
                    func.__name__ if hasattr(func, "__name__") else str(func),
                    start_time,
                )

            # Collect results
            for future in concurrent.futures.as_completed(future_to_task, timeout=timeout):
                name, func_name, start_time = future_to_task[future]
                execution_time = time.perf_counter() - start_time

                try:
                    result = future.result(timeout=0)
                    results.append(
                        ParallelResult(name=func_name, result=result, execution_time=execution_time)
                    )
                except Exception as e:
                    results.append(
                        ParallelResult(
                            name=func_name, result=None, error=e, execution_time=execution_time
                        )
                    )

        return results

    def execute_map(
        self, func: Callable, items: List[Any], timeout: Optional[float] = None
    ) -> List[ParallelResult]:
        """
        Map a function over a list of items in parallel.

        Args:
            func: Function to apply
            items: List of items to process
            timeout: Optional timeout

        Returns:
            List of ParallelResult objects
        """
        tasks = [(func, (item,), {}) for item in items]
        return self.execute_parallel(tasks, timeout)

    def execute_specialist_tasks(
        self,
        specialist_funcs: Dict[str, Callable],
        shared_context: Dict[str, Any],
        timeout: Optional[float] = 30.0,
    ) -> Dict[str, ParallelResult]:
        """
        Execute multiple specialist subagent tasks in parallel.

        Args:
            specialist_funcs: Dictionary of {specialist_name: function}
            shared_context: Context data to pass to each specialist
            timeout: Timeout in seconds (default: 30s)

        Returns:
            Dictionary of {specialist_name: ParallelResult}

        Example:
            >>> specialists = {
            ...     'career': career_specialist_func,
            ...     'finance': finance_specialist_func,
            ...     'wellness': wellness_specialist_func,
            ... }
            >>> context = {'user_id': 'user_123', 'query': 'career advice'}
            >>> results = executor.execute_specialist_tasks(specialists, context)
        """
        tasks = []
        for name, func in specialist_funcs.items():
            # Each specialist gets the shared context
            tasks.append((func, (), shared_context))

        results = self.execute_parallel(tasks, timeout)

        # Map back to specialist names
        return {name: result for name, result in zip(specialist_funcs.keys(), results)}


class AsyncToolExecutor:
    """
    Async-based tool execution for non-blocking operations.

    Useful for I/O-bound operations like network calls or file operations.
    """

    def __init__(self):
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop."""
        if self._loop is None or self._loop.is_closed():
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop

    async def _execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function asynchronously."""
        loop = self._get_loop()

        # Run in thread pool to avoid blocking
        with ThreadPoolExecutor(max_workers=1) as executor:
            return await loop.run_in_executor(executor, functools.partial(func, *args, **kwargs))

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function asynchronously and return result.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result
        """
        loop = self._get_loop()
        return loop.run_until_complete(self._execute_async(func, *args, **kwargs))

    async def execute_multiple(
        self, tasks: List[Tuple[Callable, Tuple, Dict]]
    ) -> List[ParallelResult]:
        """
        Execute multiple tasks concurrently.

        Args:
            tasks: List of (function, args, kwargs) tuples

        Returns:
            List of ParallelResult objects
        """

        async def run_task(name: str, func: Callable, args: Tuple, kwargs: Dict) -> ParallelResult:
            start_time = time.perf_counter()
            try:
                result = await self._execute_async(func, *args, **kwargs)
                return ParallelResult(
                    name=name, result=result, execution_time=time.perf_counter() - start_time
                )
            except Exception as e:
                return ParallelResult(
                    name=name, result=None, error=e, execution_time=time.perf_counter() - start_time
                )

        # Create tasks
        async_tasks = []
        for i, (func, args, kwargs) in enumerate(tasks):
            name = func.__name__ if hasattr(func, "__name__") else f"task_{i}"
            async_tasks.append(run_task(name, func, args, kwargs))

        # Execute concurrently
        return await asyncio.gather(*async_tasks)

    def run_multiple(self, tasks: List[Tuple[Callable, Tuple, Dict]]) -> List[ParallelResult]:
        """
        Synchronous interface to execute multiple tasks.

        Args:
            tasks: List of (function, args, kwargs) tuples

        Returns:
            List of ParallelResult objects
        """
        loop = self._get_loop()
        return loop.run_until_complete(self.execute_multiple(tasks))


def parallel_map(
    func: Callable, items: List[Any], max_workers: int = 4, timeout: Optional[float] = None
) -> List[Any]:
    """
    Map a function over items in parallel (convenience function).

    Args:
        func: Function to apply
        items: List of items
        max_workers: Number of parallel workers
        timeout: Optional timeout

    Returns:
        List of results (may include exceptions)

    Example:
        >>> results = parallel_map(process_user, user_ids, max_workers=8)
    """
    executor = ParallelExecutor(max_workers=max_workers)
    results = executor.execute_map(func, items, timeout)
    return [r.result if r.success else r.error for r in results]


def parallel_specialists(
    specialist_funcs: Dict[str, Callable],
    context: Dict[str, Any],
    max_workers: int = 4,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """
    Execute specialist functions in parallel (convenience function).

    Args:
        specialist_funcs: Dictionary of {name: function}
        context: Shared context to pass to all specialists
        max_workers: Number of parallel workers
        timeout: Timeout in seconds

    Returns:
        Dictionary of {name: result}

    Example:
        >>> specialists = {
        ...     'career': get_career_advice,
        ...     'finance': get_finance_advice,
        ... }
        >>> results = parallel_specialists(specialists, {'user_id': '123'})
        >>> career_result = results['career']
    """
    executor = ParallelExecutor(max_workers=max_workers)
    results = executor.execute_specialist_tasks(specialist_funcs, context, timeout)

    # Extract just the results
    return {
        name: result.result if result.success else result.error for name, result in results.items()
    }


class BatchProcessor:
    """
    Process items in batches for optimal performance.

    Balances between memory usage and parallelization efficiency.
    """

    def __init__(self, batch_size: int = 10, max_workers: int = 4):
        """
        Initialize batch processor.

        Args:
            batch_size: Number of items per batch
            max_workers: Number of parallel workers
        """
        self.batch_size = batch_size
        self.max_workers = max_workers

    def process_batches(self, items: List[Any], process_func: Callable[[Any], Any]) -> List[Any]:
        """
        Process items in batches.

        Args:
            items: List of items to process
            process_func: Function to apply to each item

        Returns:
            List of results
        """
        results = []
        executor = ParallelExecutor(max_workers=self.max_workers)

        # Process in batches
        for i in range(0, len(items), self.batch_size):
            batch = items[i : i + self.batch_size]
            batch_results = executor.execute_map(process_func, batch)
            results.extend([r.result if r.success else r.error for r in batch_results])

        return results

    def process_with_progress(
        self,
        items: List[Any],
        process_func: Callable[[Any], Any],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[Any]:
        """
        Process items with progress updates.

        Args:
            items: List of items to process
            process_func: Function to apply to each item
            progress_callback: Optional callback(completed, total)

        Returns:
            List of results
        """
        results = []
        total = len(items)
        completed = 0

        for i in range(0, len(items), self.batch_size):
            batch = items[i : i + self.batch_size]
            batch_results = parallel_map(process_func, batch, max_workers=self.max_workers)
            results.extend(batch_results)

            completed += len(batch)
            if progress_callback:
                progress_callback(completed, total)

        return results


def optimize_specialist_delegation(
    coordinator_query: str,
    specialists: Dict[str, Callable],
    user_context: Dict[str, Any],
    parallel_threshold: int = 2,
) -> Dict[str, Any]:
    """
    Intelligently decide between parallel and sequential specialist execution.

    Args:
        coordinator_query: The query being processed
        specialists: Dictionary of available specialists
        user_context: User context data
        parallel_threshold: Minimum number of specialists to trigger parallel execution

    Returns:
        Dictionary of specialist results
    """
    # If only one specialist or few specialists, execute sequentially
    if len(specialists) < parallel_threshold:
        results = {}
        for name, func in specialists.items():
            try:
                results[name] = func(**user_context)
            except Exception as e:
                results[name] = e
        return results

    # Multiple specialists - execute in parallel for better performance
    return parallel_specialists(
        specialists, user_context, max_workers=min(len(specialists), 4), timeout=30.0
    )
