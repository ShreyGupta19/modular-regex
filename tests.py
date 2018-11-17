import re
import unittest
from modexp import ModExp, ModExpEnv

class ModExpTest1(unittest.TestCase):
  def setUp(self):
    env = ModExpEnv()
    self.natural = ModExp(r'\d+', 'natural', env)
    self.positive_rational = ModExp(r'~<natural>\.~<natural>', 'positive_rational', env)

  def test_dependencies(self):
    self.assertSetEqual(self.natural.dependencies, set())
    self.assertSetEqual(self.positive_rational.dependencies, {'natural'})

  def test_positive_rationals(self):
    self.assertIsNotNone(re.fullmatch(self.positive_rational.regex(), '34.23'))
    self.assertIsNone(re.fullmatch(self.positive_rational.regex(), '34d.23'))
    self.assertIsNone(re.fullmatch(self.positive_rational.regex(), '.23'))

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
    self.assertIsNotNone(re.fullmatch(self.rational.regex(), '34.23'))
    self.assertIsNotNone(re.fullmatch(self.rational.regex(), '-34.23'))
    self.assertIsNone(re.fullmatch(self.rational.regex(), '34d.23'))
    self.assertIsNone(re.fullmatch(self.rational.regex(), '.23'))
    self.assertIsNone(re.fullmatch(self.rational.regex(), '-.23'))
    self.assertIsNone(re.fullmatch(self.rational.regex(), '34.-23'))

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
    self.assertIsNotNone(re.fullmatch(self.expr.regex(), '34 + 43'))
    self.assertIsNotNone(re.fullmatch(self.expr.regex(), '34+43'))
    self.assertIsNotNone(re.fullmatch(self.expr.regex(), '34*23'))
    self.assertIsNone(re.fullmatch(self.expr.regex(), '34.2 * 234'))

  def test_complex_exprs(self):
    self.assertIsNotNone(re.fullmatch(self.complex_expr.regex(), '(23+43) / (23+2)'))
    self.assertIsNotNone(re.fullmatch(self.complex_expr.regex(), '(23+43)/(23+2)'))
    self.assertIsNone(re.fullmatch(self.complex_expr.regex(), '23 / (23+2)'))
    self.assertIsNone(re.fullmatch(self.complex_expr.regex(), '(23) / (23+2)'))
    self.assertIsNone(re.fullmatch(self.complex_expr.regex(), '(23+2)/(23)'))

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

class ModExpTestChanges(unittest.TestCase):
  def setUp(self):
    env = ModExpEnv()
    self.number = ModExp(r'-?\d+(\.\d+)?', 'number', env)
    self.operator = ModExp(r'(\+|-|\/|\*)', 'operator', env)
    self.expr = ModExp(r'~<number>\s?~<operator>\s?~<number>', 'expr', env)
    self.number = ModExp(r'\d+', 'number', env)

  def test_dependencies(self):
    self.assertSetEqual(self.number.dependencies, set())
    self.assertSetEqual(self.operator.dependencies, set())
    self.assertSetEqual(self.expr.dependencies, {'number', 'operator'})

  def test_exprs(self):
    self.assertIsNotNone(re.fullmatch(self.expr.regex(), '34 + 43'))
    self.assertIsNotNone(re.fullmatch(self.expr.regex(), '34+43'))
    self.assertIsNotNone(re.fullmatch(self.expr.regex(), '34*23'))
    self.assertIsNone(re.fullmatch(self.expr.regex(), '34.2 * 234'))
    self.assertIsNone(re.fullmatch(self.expr.regex(), '342 * 23.4'))
    self.assertIsNone(re.fullmatch(self.expr.regex(), '34.2 / 23.4'))
    self.assertIsNone(re.fullmatch(self.expr.regex(), '-34.2 / 23.4'))
    self.assertIsNone(re.fullmatch(self.expr.regex(), '-34.2 / -23.4'))

if __name__ == '__main__':
  unittest.main()