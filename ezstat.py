#!/usr/bin/env python3

"""Easy statistics

The main class `Statistics` just extends dict{str:function},
function here will act on the object of statistics.
The values of dict have not to be a function.
If it is a string, then the attribute of object will be called.

Please see the following example and the function `_call`, the underlying implementation.

Pseudo codes:
    ```
    if s: str
        f = getattr(obj, s)
        if f: function
            r = f()
        else
            r = f
    elif s: function
        r = s(obj)
    elif s is number:
        r = s
    ```

Example:

    >>> import numpy as np

    >>> T = np.random.random((100,100))
    >>> s = Statistics({'mean': lambda x: np.mean(np.mean(x, axis=1)), 'max': lambda x: np.max(np.mean(x, axis=1)), 'shape':'shape'})
    >>> print(s(T))
    >>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape': (100, 100)}

    >>> print(s(T, split=True)) # split the tuple if it needs
    >>> {mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape-0': 100, 'shape-1': 100}

`MappingStatistics` subclasses Statistics. It only copes with iterable object,
and maps it to an array by a "key" function.

Example:

    >>> s = MappingStatistics('mean', {'mean':np.mean, 'max':np.max})
    >>> print(s(T))
    >>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957}

In the exmaple, 'mean', an attribute of T, maps T to a 1D array.


Advanced Usage:
`Statistics` acts on a list/tuple of objects iteratively, gets a series of results,
forming an object of pandas.DataFrame.

    history = pd.DataFrame(columns=s.keys())
    for obj in objs:
        history = history.append(s(obj), ignore_index=True)

"""


def _call(s, obj):
    """Core function of ezstat
    
    s {function | string} -- Statistics
    obj -- object of statistics
    
    An extension for s(x) or x.s
    If s is an string, then it only returns x.s() if callable, otherwise x.s.
    """
    if isinstance(s, str):
        if not hasattr(obj, s):
            raise ValueError(f"the object has no attribute '{s}'")
        f = getattr(obj, s)
        if callable(f):
            r = f()
        else:
            r = f
    elif callable(s):
        r = s(obj)
    elif isinstance(s, (int, float, tuple)):
        # deprecated
        r = s
    else:
        raise TypeError(f"The type of the value corresponding to key `{k}` is not permissible!") 

    return r

class Statistics(dict):
    def __call__(self, *args, **kwargs):
        return self.do(*args, **kwargs)

    def do(self, obj, split=False):
        """
        execute a staistics

        Arguments:
            obj {object} -- an object (population) of statistics
            split {bool} -- if True, it will split the tuple-type statistics result to numbers
        
        Returns:
            dict

        Example:
        >>> import numpy as np

        >>> T = np.random.random((100,100))
        >>> s = Statistics({'mean': lambda x: np.mean(np.mean(x, axis=1)), 'max': lambda x: np.max(np.mean(x, axis=1)), 'shape':'shape'})
        >>> print(s(T))
        >>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape': (100, 100)}

        >>> print(s(T, split=True)) # split the tuple if it needs
        >>> {mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape-0': 100, 'shape-1': 100}
        """
        res = {}
        for k, s in self.items():
            # if s is True and isinstance(k, str):
            #     r = _call(k, obj)
            r = _call(s, obj)
  
            if split and isinstance(r, tuple):
                for i, ri in enumerate(r):
                    res[f'{k}-{i}'] = ri
            else:
                res[k] = r
        return res

    def dox(self, objs):
        data = map(s, objs)
        return pd.DataFrame(data=data, columns=s.keys())


class MappingStatistics(Statistics):
    """Just a wrapper of `Statistics`

    Only recommanded to cope with iterable object of statistics.
    It will transfrom the object to array by `key` (functional attribute) before doing statistics.
    
    Extends:
        Statistics

    Example:
    >>> import numpy as np

    >>> T = np.random.random((100,100))
    >>> s = MappingStatistics('mean', {'mean':np.mean, 'min':np.min})
    >>> print(s(T))
    >>> {'mean': 0.4995186088546244, 'min': 0.39975807140966796}

    In the exmaple, 'mean', an attribute of np.ndarray, maps each row of T to a number.
    As a result, the object of statistics is a 1D array.
    """

    def __init__(self, key=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._key = key

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, v):
        self._key = v
    
    def do(self, obj, split=False):
        """
        The object of statistics should be iterable
        """
        if self.key:
            obj = np.array([_call(self.key, k) for k in obj]) # should be an array of numbers
        return super().do(obj, split=split)

