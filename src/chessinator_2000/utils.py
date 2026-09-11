from collections.abc import Callable, Iterable


def delete[K, V](*key: K) -> Callable[[frozendict[K, V]], frozendict[K, V]]:
    def fn(d: frozendict[K, V]) -> frozendict[K, V]:
        return frozendict((k, v) for k, v in d.items() if k not in key)  # pyright: ignore[reportCallIssue]

    return fn


def set[K, V](key: K, value: V) -> Callable[[frozendict[K, V]], frozendict[K, V]]:
    def fn(d: frozendict[K, V]) -> frozendict[K, V]:
        return d | {key: value}

    return fn


def identity[T](x: T, /) -> T:
    return x


def groupby[T, K, V](
    iterable: Iterable[T], key: Callable[[T], K], value: Callable[[T], V] = identity
) -> frozendict[K, Iterable[V]]:
    tuples = [(key(t), value(t)) for t in iterable]
    keys = {k for k, _ in tuples}

    def _values(k: K) -> Iterable[V]:
        return tuple(v for _k, v in tuples if _k == k)

    return frozendict((k, _values(k)) for k in keys)  # pyright: ignore[reportCallIssue]
