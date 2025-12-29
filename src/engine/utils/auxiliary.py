from typing import Any, Callable


def insertion_sort(arr: list[Any], size: Callable[[Any], int]) -> None:
    n = len(arr)
    if n <= 1:
        return
    for i in range(1, n, 1):
        key, j = arr[i], i - 1
        while j >= 0 and size(key) < size(arr[j]):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
