class Vec2:
  def __init__(self, x, y):
    self._x = x
    self._y = y

  # x and y setters and getters
  @property
  def x(self):
    return self._x
  
  @property
  def y(self):
    return self._y

  @x.setter
  def x(self, value):
    self._x = value
  
  @y.setter
  def y(self, value):
    self._y = value
  
  # w and h setters and getters
  @property
  def w(self):
    return self._x
  
  @property
  def h(self):
    return self._y

  @w.setter
  def w(self, value):
    self._x = value
  
  @h.setter
  def h(self, value):
    self._y = value