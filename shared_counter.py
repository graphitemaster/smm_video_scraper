
from multiprocessing import Value, Lock

class SharedCounter:
  def __init__(self, initial_value=0):
    self._value = Value('i', initial_value)
    self._lock = Lock()

  def increment(self):
    with self._lock:
      self._value.value += 1
  
  def value(self):
    with self._lock:
      return self._value.value