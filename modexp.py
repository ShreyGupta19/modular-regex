import re
import unittest

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
  def __init__(self, lazy=False):
    self._expressions = {}
    self.lazy = lazy

  def get_regex(self, name):
    return self._expressions[name].regex

class ModExp:
  def __init__(self, regex_str, name, env=None):
    self.raw_regex = regex_str
    self.name = name
    self.dependencies = set()
    self.env = env if env is not None else ModExpEnv()
    self.env._expressions[name] = self

    if not self.env.lazy:
      self.regex  # Force calculation of the lazy property.

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

if __name__ == '__main__':
  class ModExpTest1(unittest.TestCase):
    def setUp(self):
      env = ModExpEnv()
      self.natural = ModExp(r'\d+', 'natural', env)
      self.positive_rational = ModExp(r'~<natural>\.~<natural>', 'positive_rational', env)

    def test_dependencies(self):
      self.assertSetEqual(self.natural.dependencies, set())
      self.assertSetEqual(self.positive_rational.dependencies, {'natural'})

    def test_positive_rationals(self):
      self.assertIsNotNone(re.match(self.positive_rational.regex, '34.23'))
      self.assertIsNone(re.match(self.positive_rational.regex, '34d.23'))
      self.assertIsNone(re.match(self.positive_rational.regex, '.23'))
  
  class ModExpTest2(unittest.TestCase):
    def setUp(self):
      env = ModExpEnv()
      self.natural = ModExp(r'\d+', 'natural', env)
      self.integer = ModExp(r'-?\d+', 'integer', env)
      self.rational = ModExp(r'~<integer>\.~<natural>', 'rational', env)

    def test_dependencies(self):
      self.assertSetEqual(self.natural.dependencies, set())
      self.assertSetEqual(self.integer.dependencies, set())
      self.assertSetEqual(self.rational.dependencies, {'natural', 'integer'})

    def test_rationals(self):
      self.assertIsNotNone(re.match(self.rational.regex, '34.23'))
      self.assertIsNotNone(re.match(self.rational.regex, '-34.23'))
      self.assertIsNone(re.match(self.rational.regex, '34d.23'))
      self.assertIsNone(re.match(self.rational.regex, '.23'))
      self.assertIsNone(re.match(self.rational.regex, '-.23'))
      self.assertIsNone(re.match(self.rational.regex, '34.-23'))

  class ModExpTest3(unittest.TestCase):
    def setUp(self):
      env = ModExpEnv()
      self.natural = ModExp(r'\d+', 'natural', env)
      self.operator = ModExp(r'(\+|-|\/|\*)', 'operator', env)
      self.expr = ModExp(r'~<natural>\s?~<operator>\s?~<natural>', 'expr', env)
      self.complex_expr = ModExp(r'\(~<expr>\)\s?~<operator>\s?\(~<expr>\)', 'complex_expr', env)

    def test_dependencies(self):
      self.assertSetEqual(self.natural.dependencies, set())
      self.assertSetEqual(self.operator.dependencies, set())
      self.assertSetEqual(self.expr.dependencies, {'natural', 'operator'})
      self.assertSetEqual(self.complex_expr.dependencies, {'expr', 'operator', 'natural'})

    def test_exprs(self):
      self.assertIsNotNone(re.match(self.expr.regex, '34 + 43'))
      self.assertIsNotNone(re.match(self.expr.regex, '34+43'))
      self.assertIsNotNone(re.match(self.expr.regex, '34*23'))
      self.assertIsNone(re.match(self.expr.regex, '34.2 * 234'))

    def test_complex_exprs(self):
      self.assertIsNotNone(re.match(self.complex_expr.regex, '(23+43) / (23+2)'))
      self.assertIsNotNone(re.match(self.complex_expr.regex, '(23+43)/(23+2)'))
      self.assertIsNone(re.match(self.complex_expr.regex, '23 / (23+2)'))
      self.assertIsNone(re.match(self.complex_expr.regex, '(23) / (23+2)'))
      self.assertIsNone(re.match(self.complex_expr.regex, '(23+2)/(23)'))

  class ModExpTestLazy(unittest.TestCase):
    def setUp(self):
      pass

    def test_lazy_eval(self):
      try:
        env = ModExpEnv(lazy=True)
        complex_expr = ModExp(r'\(~<expr>\)\s?~<operator>\s?\(~<expr>\)', 'complex_expr', env)
        expr = ModExp(r'~<natural>\s?~<operator>\s?~<natural>', 'expr', env)
        natural = ModExp(r'\d+', 'natural', env)
        operator = ModExp(r'(\+|-|\/|\*)', 'operator', env)
      except KeyError:
        self.fail('Lazy evaluation raised KeyError unexpectedly.')

    def test_nonlazy_eval(self):
      with self.assertRaises(KeyError):
        env = ModExpEnv()
        complex_expr = ModExp(r'\(~<expr>\)\s?~<operator>\s?\(~<expr>\)', 'complex_expr', env)
        expr = ModExp(r'~<natural>\s?~<operator>\s?~<natural>', 'expr', env)
        natural = ModExp(r'\d+', 'natural', env)
        operator = ModExp(r'(\+|-|\/|\*)', 'operator', env)
  
  unittest.main()
