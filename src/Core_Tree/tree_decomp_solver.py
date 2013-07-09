"""
FourVoices -- A music generator. 
Copyright (C) 2012 Eric Kim <erickim555@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

""" TO DO
  ===============================
  1.) Finish init_problem()
      - Add constraints between mega-variables
  ===============================
"""

import copy

import Core_Tree.constraint

# x = "S, A, T, B"
# y = "S, A, T, B"
# Order by "s3, s2, s1, a3, ..., t3, ..., b3, ..."
def myComparator(x, y):
  x1 = __voiceToNum__(x)
  y1= __voiceToNum__(y)
  if x1 > y1: return 1
  if x1 == y1:
    x_num = int(x[1:])
    y_num = int(y[1:])
    return x_num.__cmp__(y_num)
  # x1 < y1
  return -1

# translates "S, A, T, B" to "0, 1, 2, 3"
def __voiceToNum__(voice):
  lowerCase = voice.lower() # Just in case we get something like "S3" versus "s3"
  return {"s": 0,
          "a": 1,
          "t": 2,
          "b": 3}[lowerCase[0]] # Grab first letter


# Attempts to find a solution to the Tree-Structured CSP
# subproblems := a list of Problem() instances representing the sub-problems
# mega_constraints := a dict mapping mega-variables to mega-constraints 
def solve_iter(subproblems, mega_constraints):
  mega_vars = init_mega_vars(subproblems)
  tree_solver = Tree_Solver()
  problem = Core_Tree.constraint.Problem(tree_solver)    # Use the Tree-Structured Solver
  init_vars(problem, mega_vars)
  init_constraints(problem, mega_constraints)
  return problem.getSolutionIter()
    
# Initializes the problem
# Adds variables/domains to problem
def init_vars(problem, mega_vars):
  for mega_var in mega_vars:
    mega_var_cpy = list(mega_var)
    mega_var_cpy.sort(lambda x, y : myComparator(x, y))
    mega_var_cpy = tuple(mega_var_cpy)
    problem.addVariable(mega_var_cpy, mega_vars[mega_var])

def init_constraints(problem, mega_constraints):
  for key in mega_constraints.keys():
    for constraint in mega_constraints[key]:
      problem.addConstraint(constraint, key)
  
# returns a dict mapping variables to domains
def init_mega_vars(subproblems):
  mega_vars = {}
  for subproblem in subproblems:
    for subsolution in subproblem.getSolutionIter():
      tag = tuple(subproblem._variables)
      if mega_vars.has_key(tag):
        domain = mega_vars[tag]
        domain.append(subsolution)
        mega_vars[tag] = domain
      else:
        mega_vars[tag] = [subsolution]
  return mega_vars
  
  
class Tree_Solver(Core_Tree.constraint.Solver):
  
  def _makeConstraintDict(self, constraints):
    new_dict = {}
    const_relations = [x[1] for x in constraints]
    for x in const_relations:
      new_dict[x] = []
    for tuple in constraints:
      old_list = new_dict[tuple[1]]
      old_list.append(tuple[0])
    return new_dict  
  def _getRoot(self, domains, constraints, vconstraints):
    keys = domains.keys()
    keys.sort(lambda a, b : int(a[0][1:]).__cmp__(int(b[0][1:])))
    return keys[0]
  def _orderVars(self, root, vars, const_dict):
    result = []
    stack = [root]
    while( len(stack) != 0):
      node = stack.pop()
      result.append(node)
      children = self._getChildren(node, const_dict)
      for child in children:
        if (child not in stack) and (child not in result):
          stack.append(child)
    return result  
  def _getChildren(self, node, const_dict):
    children = []
    for key in const_dict.keys():
      if node in key:
        children.extend([x for x in key if (x != node)])
    return children
  
  def getSolution(self, domains, constraints, vconstraints):
    print "not defined"
  
  def getSolutions(self, domains, constraints, vconstraints):
    print "nope"
  
  """
  Return an iterator for the solutions of the given problem

  @param domains: Dictionary mapping variables to domains
  @type  domains: dict
  @param constraints: List of pairs of (constraint, variables)
  @type  constraints: list
  @param vconstraints: Dictionary mapping variables to a list of
                       constraints affecting the given variables.
  @type  vconstraints: dict
  """
  
  """ 
  From the textbook, page 180:
  1.) Choose any variable as the root of the tree, and order the variables from the root
      to the leaves in such a way that every node's parent in the tree precedes it in the 
      ordering. Label the variables X(1), ..., X(n) in order. Now, every variable except
      the root has exactly one parent variable.
  2.) For j from n down to 2, apply arc consistency to the arc ( X(i), X(j) ), where X(i)
      is the parent of X(j), removing values from DOMAIN[X(i)] as necessary.
  3.) For j from 1 to n, assign any value for X(j) consistent with the value assigned for
      X(i), where X(i) is the parent of X(j).
      
  """
  def getSolutionIter(self, domains, constraints, vconstraints):
    assignments = {}
    root = self._getRoot(domains, constraints, vconstraints)
    const_dict = self._makeConstraintDict(constraints)
    vars_ordered = self._orderVars(root, domains.keys(), const_dict) 
    n = len(vars_ordered)
    for j in range(n-1, 0, -1):
      x_i = vars_ordered[j - 1]
      x_j = vars_ordered[j]
      arc = ( x_i, x_j )
      self.makeArcConsistent(arc, domains, const_dict)
    root_tag = vars_ordered[0]
    solution_history = []
    """
    Pseudo code for iterator:
    n = number of vars
    for j in range(1, n):
      
    
    """
    for root_value in domains[root_tag]:
      stack = []
      history = []
      assignments = {}
      assignments[root_tag] = root_value
      stack.append(copy.deepcopy(assignments))
      history.append(copy.deepcopy(assignments))
      while( len(stack) != 0 ):
        assignments = stack.pop()
        for j in range(1, n):
          x_i = vars_ordered[j - 1]
          x_j = vars_ordered[j]
          parent_value = assignments[x_i]
          consistent_val_iter = self.chooseConsistentValue_iter(x_j, x_i, domains, const_dict, parent_value)
          assignments[x_j] = consistent_val_iter.next()
          for value in consistent_val_iter:
            new_assignments = copy.deepcopy(assignments)
            new_assignments[x_j] = value
            if new_assignments not in history:
              stack.append(new_assignments)
              history.append(copy.deepcopy(new_assignments))
        if assignments not in solution_history:
          solution_history.append(assignments)
          yield assignments

  def getSolutionIter_single(self, domains, constraints, vconstraints):
    assignments = {}
    root = self._getRoot(domains, constraints, vconstraints)
    const_dict = self._makeConstraintDict(constraints)
    vars_ordered = self._orderVars(root, domains.keys(), const_dict)
    n = len(vars_ordered)
    for j in range(n-1, 0, -1):
      x_i = vars_ordered[j - 1]
      x_j = vars_ordered[j]
      arc = ( x_i, x_j )
      self.makeArcConsistent(arc, domains, const_dict)
    for j in range(n):
      if j == 0:    # Special case, the root node has no parents, so we can assign any value to it
        root_tag = vars_ordered[0]
        assignments[root_tag] = domains[root_tag][0]  # For now, just assign the first value
        continue
      x_i = vars_ordered[j - 1]
      x_j = vars_ordered[j]
      parent_value = assignments[x_i]
      assignments[x_j] = self.chooseConsistentValue(x_j, x_i, domains, const_dict, parent_value)
    return assignments
    
  """
  Return a value for variable x_j that is consistent with variable x_i (the parent)
  In other words, return a value for x_j that makes the arcs ( x_j, x_i ), ( x_i, x_j ) consistent.
  @param  x_j:          Variable
  @type   x_j:          tuple
  @param  x_i:          Variable that is the parent of x_j
  @type   x_i:          tuple
  @param  domains:      Domains of all Variables
  @type   domains:      dict
  @param  vconstraints: Dictionary mapping variables to constraints connecting the variables
  @type   vconstraints: dict
  """
  def chooseConsistentValue(self, x_j, x_i, domains, const_dict, parent_value):  
    for value in domains[x_j]: 
      #if self._isConsistent( (x_j, value) , (x_i, parent_value) , const_dict) and self._isConsistent( (x_i, parent_value) , (x_j, value) , const_dict):
      if self._isConsistent( (x_i, parent_value) , (x_j, value) , const_dict):
        return value
    ### We should never get here!!!
    print "ERROR: Somehow, there was not any consistent value for x_j. Exiting."
    exit(1) 
  
  def chooseConsistentValue_iter(self, x_j, x_i, domains, const_dict, parent_value):
    for value in domains[x_j]: 
      if self._isConsistent( (x_i, parent_value) , (x_j, value) , const_dict):
        yield value
  
  """
  Returns true if the assignment of x, y is consistent with the constraints.
  @param  x:    A tuple ( <var_tag> , <value> )
  @type   x:    list
  @param  y:    A tuple ( <var_tag>, <value> )
  @type   y:    list
  @param  const_dict:  dict mapping variables to constraints relating them
  @type   const_dict:  dict
  """
  def _isConsistent(self, x, y, const_dict):
    x_tag = x[0]
    y_tag = y[0]
    x_val = x[1]
    y_val = y[1]
    constraints = []
    # Two variables with no constraints relating them are automatically 
    # consistent 
    if not(const_dict.has_key( (x_tag, y_tag) )):
      return True
    constraints.extend(const_dict[ (x_tag, y_tag) ])
    if len(constraints) != 0:
      for constraint in constraints:
        if constraint._func(x_val, y_val) == False:
          return False
    return True


  def _isConsistent_2ways(self, x, y, const_dict):
    x_tag = x[0]
    y_tag = y[0]
    x_val = x[1]
    y_val = y[1]
    constraints = []
    permutations = ( (x_tag, y_tag) , (y_tag, x_tag) )
    for p in permutations:
      if p in const_dict.keys():
        constraints.append( (permutations.index(p) , const_dict[p]) )
    if len(constraints) != 0:
      for tuple in constraints:
        if tuple[0] == 0:
          constraints = tuple[1]
          for constraint in constraints:
            if constraint._func(x_val, y_val) == False:
              return False
        else:   # constraint[0] == 1:
          constraints = tuple[1]
          for constraint in constraints:
            if constraint._func(y_val, x_val) == False:
              return False
    return True
  
  """
  Returns a true if a domain has been modified, false otherwise.
  Note that this function MUTATES domains.
  2.) For j from n down to 2, apply arc consistency to the arc ( X(i), X(j) ), where X(i)
      is the parent of X(j), removing values from DOMAIN[X(i)] as necessary.
  """
  
  def makeArcConsistent(self, arc, domains, const_dict):
    x_i = arc[0]
    x_j = arc[1]
    x_i_domain = copy.deepcopy(domains[x_i])
    x_j_domain = domains[x_j]
    is_domain_changed = False
    for x_i_value in x_i_domain:
      is_arc_consistent = False
      for x_j_value in x_j_domain:
        if self._isConsistent((x_i, x_i_value), (x_j, x_j_value), const_dict):
          is_arc_consistent = True
          break
      if not(is_arc_consistent):
        is_domain_changed = True
        domains[x_i].remove(x_i_value)  #  == x_i_domain.remove(x_i_value)
    return is_domain_changed
  
  
  """
  def makeArcConsistent(self, arc, domains, const_dict):
    x_i = arc[0]
    x_j = arc[1]
    x_i_domain = domains[x_i]   ### <== IINTERESTING - not doing a deepcopy resulted in bad behavior.
    ### I suspect there is a Python subtlety with modifying a list while you're iterating over it...
    ### I should investigate this further later.
    x_j_domain = domains[x_j]
    is_domain_changed = False
    for x_i_value in x_i_domain:
      is_arc_consistent = False
      for x_j_value in x_j_domain:
        if self._isConsistent((x_i, x_i_value), (x_j, x_j_value), const_dict):
          is_arc_consistent = True
          break
      if not(is_arc_consistent):
        is_domain_changed = True
        domains[x_i].remove(x_i_value)  #  == x_i_domain.remove(x_i_value)
    return is_domain_changed  
  """