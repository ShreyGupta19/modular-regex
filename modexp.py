import re

MOD_EXP_FORMAT = r'~<([a-z]+)>'

def lazy_property(fn):
  attr_name = '_lazy_' + fn.__name__

  @property
  def _lazy_property(self):
    if not hasattr(self, attr_name):
      setattr(self, attr_name, fn(self))
    return getattr(self, attr_name)
  return _lazy_property

class ModExpEnv:
  def __init__(self):
    self._expressions = {}

  def get_regex(self, name):
    return self._expressions[name].regex

class ModExp:
  def __init__(self, regex_str, name, env=None):
    self.raw_regex = regex_str
    self.name = name
    self.dependencies = set()
    self.env = env if env is not None else ModExpEnv()
    self.env._expressions[name] = self

  @lazy_property
  def regex(self):
    def lookup_expr(match_obj):
      expr_name = match_obj.group(1)
      if expr_name not in self.env._expressions:
        raise KeyError('Modular Expression \'{}\'not found.'.format(expr_name))
      self.dependencies.add(expr_name)
      child_modexp = self.env._expressions[expr_name]
      regex = child_modexp.regex
      self.dependencies |= child_modexp.dependencies
      return child_modexp.regex

    return re.sub(MOD_EXP_FORMAT, lookup_expr, self.raw_regex)
