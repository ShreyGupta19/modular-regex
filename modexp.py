import re

class ModExpEnv:
  def __init__(self, lazy=False):
    self._expressions = {}
    self.lazy = lazy

  def get_regex(self, name):
    return self._expressions[name].regex()


MOD_EXP_ENV_GLOBAL = ModExpEnv()
MOD_EXP_FORMAT = r'~<([A-Za-z0-9\_\.\-]+)>'

class ModExp:
  def __init__(self, regex_str, name, env=None):
    self.raw_regex = regex_str
    self.name = name
    self.dependencies = set()
    self.env = env if env is not None else MOD_EXP_ENV_GLOBAL
    self.env._expressions[name] = self
    self._compiled_regex = None

    if not self.env.lazy:
      self.regex(force=True)

  def _propagate_changes(self):
    for modexp in self.env._expressions.values():
      if self.name in modexp.dependencies:
        modexp.regex(force=True)

  def regex(self, force=False):
    if self._compiled_regex is None or force:
      def lookup_expr(match_obj):
        expr_name = match_obj.group(1)
        if expr_name not in self.env._expressions:
          raise KeyError('Modular Expression \'{}\'not found.'.format(expr_name))
        self.dependencies.add(expr_name)
        child_modexp = self.env._expressions[expr_name]
        regex = '(' + child_modexp.regex() + ')'
        self.dependencies |= child_modexp.dependencies
        return regex

      self._compiled_regex = re.sub(MOD_EXP_FORMAT, lookup_expr, self.raw_regex)
      self._propagate_changes()

    return self._compiled_regex
