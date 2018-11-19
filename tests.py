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
    self.operator = ModExp(r'\+|-|\/|\*', 'operator', env)
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
      operator = ModExp(r'\+|-|\/|\*', 'operator', env)
      self.assertIsNone(env._expressions['complex_expr']._compiled_regex)
      self.assertIsNone(env._expressions['expr']._compiled_regex)
      self.assertIsNone(env._expressions['natural']._compiled_regex)
      self.assertIsNone(env._expressions['operator']._compiled_regex)
      complex_expr.regex()
    except KeyError:
      self.fail('Lazy evaluation raised KeyError unexpectedly.')

  def test_nonlazy_eval(self):
    with self.assertRaises(KeyError):
      env = ModExpEnv()
      complex_expr = ModExp(r'\(~<expr>\)\s?~<operator>\s?\(~<expr>\)', 'complex_expr', env)
      expr = ModExp(r'~<natural>\s?~<operator>\s?~<natural>', 'expr', env)
      natural = ModExp(r'\d+', 'natural', env)
      operator = ModExp(r'\+|-|\/|\*', 'operator', env)

class ModExpTestChanges(unittest.TestCase):
  def setUp(self):
    env = ModExpEnv()
    self.number = ModExp(r'-?\d+(\.\d+)?', 'number', env)
    self.operator = ModExp(r'\+|-|\/|\*', 'operator', env)
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

class ModExpTestGlobalEnv(unittest.TestCase):
  def setUp(self):
    self.natural = ModExp(r'\d+', 'natural')
    self.integer = ModExp(r'-?\d+', 'integer')
    self.rational = ModExp(r'~<integer>\.~<natural>', 'rational')

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

class ModExpTestMultiEnv(unittest.TestCase):
  def setUp(self):
    env1 = ModExpEnv()
    self.segment1 = ModExp(r'\d{3}', 'segment', env1)
    self.long_segment1 = ModExp(r'\d{4}', 'long_segment', env1)
    self.delimiter1 = ModExp(r'\-|\.|\s', 'delimiter', env1)
    self.entity1 = ModExp(r'~<segment>~<delimiter>~<segment>~<delimiter>~<long_segment>', 'entity', env1) 

    env2 = ModExpEnv()
    self.segment2 = ModExp(r'[A-Za-z0-9\.]+', 'segment', env2)
    self.long_segment2 = ModExp(r'[A-Za-z0-9\.]*[A-Za-z0-9]\.(com|edu|org|net)', 'long_segment', env2)
    self.delimiter2 = ModExp(r'@', 'delimiter', env2)
    self.entity2 = ModExp(r'~<segment>~<delimiter>~<long_segment>', 'entity', env2)

  def test_env1(self):
    self.assertIsNotNone(re.fullmatch(self.entity1.regex(), '123-456-7890'))
    self.assertIsNotNone(re.fullmatch(self.entity1.regex(), '123.456.7890'))
    self.assertIsNone(re.fullmatch(self.entity1.regex(), 'abc.def.ghij'))
    self.assertIsNone(re.fullmatch(self.entity1.regex(), 'abcdef@gmail.com'))
    self.assertIsNone(re.fullmatch(self.entity1.regex(), '01abcdef@gmail.com'))
    self.assertIsNone(re.fullmatch(self.entity1.regex(), 'abc.def@gmail.com'))

  def test_env2(self):
    self.assertIsNotNone(re.fullmatch(self.entity2.regex(), 'abcdef@gmail.com'))
    self.assertIsNotNone(re.fullmatch(self.entity2.regex(), '01abcdef@gmail.com'))
    self.assertIsNotNone(re.fullmatch(self.entity2.regex(), 'abc.def@gmail.com'))
    self.assertIsNone(re.fullmatch(self.entity2.regex(), '123-456-7890'))
    self.assertIsNone(re.fullmatch(self.entity2.regex(), '123.456.7890'))
    self.assertIsNone(re.fullmatch(self.entity2.regex(), 'abc.def.ghij'))

class ModExpTestCycles(unittest.TestCase):
  def test_2_cycle_nonlazy(self):
    with self.assertRaises(ValueError):
      env = ModExpEnv()
      ModExp(r'-?\d+(\.\d+)?', 'expr', env)
      ModExp(r'~<expr>\+~<expr>', 'complex_expr', env)
      ModExp(r'(-?\d+(\.\d+)?)|~<complex_expr>', 'expr', env)

  def test_2_cycle_lazy(self):
    with self.assertRaises(ValueError):
      env = ModExpEnv(lazy=True)
      ModExp(r'~<expr2>', 'expr1', env)
      expr2 = ModExp(r'~<expr1>', 'expr2', env)
      expr2.regex()

  def test_self_cycle_nonlazy(self):
    with self.assertRaises(ValueError):
      env = ModExpEnv()
      ModExp(r'-?\d+(\.\d+)?', 'expr', env)
      ModExp(r'~<expr>', 'expr', env)

  def test_self_cycle_lazy(self):
    with self.assertRaises(ValueError):
      env = ModExpEnv(lazy=True)
      expr = ModExp(r'~<expr>', 'expr', env)
      expr.regex()

  def test_self_deep_cycle_nonlazy(self):
    with self.assertRaises(ValueError):
      env = ModExpEnv()
      ModExp(r'\d', 'a', env)
      ModExp(r'~<a>', 'b', env)
      ModExp(r'~<b>', 'c', env)
      ModExp(r'~<c>', 'd', env)
      ModExp(r'~<d>', 'a', env)

  def test_self_deep_cycle_lazy(self):
    with self.assertRaises(ValueError):
      env = ModExpEnv(lazy=True)
      ModExp(r'\d', 'a', env)
      ModExp(r'~<a>', 'b', env)
      ModExp(r'~<b>', 'c', env)
      ModExp(r'~<c>', 'd', env)
      a = ModExp(r'~<d>', 'a', env)
      a.regex()

if __name__ == '__main__':
  unittest.main()
